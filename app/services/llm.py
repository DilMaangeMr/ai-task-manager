import json
import logging
from datetime import date

from anthropic import Anthropic, APIError
from pydantic import BaseModel, Field, ValidationError

from app.config import settings

log = logging.getLogger("llm")
client = Anthropic(api_key=settings.anthropic_api_key)


class LLMError(Exception):
    """Raised when the model call or its output cannot be used."""


# ---------- shapes we expect back (the validation contract) ----------
class Subtask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    minutes: int = Field(gt=0, le=480)


class Breakdown(BaseModel):
    subtasks: list[Subtask] = Field(min_length=1, max_length=10)


class Pick(BaseModel):
    task_id: int
    reason: str


class OverwhelmedPlan(BaseModel):
    essential: list[Pick] = Field(max_length=3)
    message: str


# ---------- helpers ----------
def _ask(system: str, user: str, max_tokens: int = 800) -> str:
    try:
        resp = client.messages.create(
            model=settings.llm_model,
            max_tokens=max_tokens,
            temperature=0.3,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
    except APIError as e:
        raise LLMError(f"LLM call failed: {e}") from e
    log.info("tokens in=%s out=%s", resp.usage.input_tokens, resp.usage.output_tokens)
    return resp.content[0].text


def _extract_json(text: str) -> dict:
    """Models sometimes wrap JSON in prose or code fences, so cut out the {...}."""
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found")
    return json.loads(text[start : end + 1])


def _ask_validated(system: str, user: str, model_cls):
    """Ask, parse, validate. Retry once with the error fed back to the model."""
    last_error = ""
    for attempt in range(2):
        prompt = user if not last_error else (
            f"{user}\n\nYour previous reply was invalid ({last_error}). "
            "Reply again with valid JSON only."
        )
        text = _ask(system, prompt)
        try:
            return model_cls.model_validate(_extract_json(text))
        except (ValueError, ValidationError) as e:
            last_error = str(e)[:200]
            log.warning("invalid LLM output (attempt %s): %s", attempt + 1, last_error)
    raise LLMError("The model did not return valid output")


# ---------- feature 1: break a task into steps ----------
BREAKDOWN_SYSTEM = """You are a planning assistant inside a task manager.
Break the user's task into 3 to 7 concrete, ordered steps. Each step must be
small enough to finish in one sitting. Give a realistic time estimate in
minutes for each step.
Reply with JSON only, no other text, exactly in this shape:
{"subtasks": [{"title": "...", "minutes": 30}]}"""


def break_down(title: str, due: date | None, estimate_minutes: int | None) -> Breakdown:
    user = f"Task: {title}\nDue: {due or 'no date'}\nMy own time estimate: {estimate_minutes or 'unknown'} minutes"
    return _ask_validated(BREAKDOWN_SYSTEM, user, Breakdown)


# ---------- feature 2: "I'm overwhelmed today" ----------
OVERWHELMED_SYSTEM = """You help an overwhelmed person decide what matters today.
From the task list, choose at most 3 essential tasks. Hard deadlines and
nearer due dates matter most. Use only task ids from the list.
Reply with JSON only, no other text, exactly in this shape:
{"essential": [{"task_id": 1, "reason": "..."}], "message": "a short, kind note"}"""


def overwhelmed(tasks: list[dict], hours_available: float | None) -> OverwhelmedPlan:
    user = (
        f"Today is {date.today()}. Hours available: {hours_available or 'unknown'}.\n"
        f"Tasks:\n{json.dumps(tasks, default=str, indent=2)}"
    )
    plan = _ask_validated(OVERWHELMED_SYSTEM, user, OverwhelmedPlan)
    valid_ids = {t["id"] for t in tasks}
    # Guardrail: never trust the model's ids, so drop anything we did not send
    plan.essential = [p for p in plan.essential if p.task_id in valid_ids]
    return plan
