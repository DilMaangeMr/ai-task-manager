import torch
from torch import nn

torch.manual_seed(0)

# Fake history: 200 tasks
estimate = torch.rand(200, 1) * 115 + 5            # 5 to 120 minutes
actual = 1.5 * estimate + 10 + torch.randn(200, 1) * 8

# Scale to small numbers so training is stable
x = estimate / 100
y = actual / 100

model = nn.Linear(1, 1)                            # y = w*x + b
loss_fn = nn.MSELoss()
optimizer = torch.optim.SGD(model.parameters(), lr=0.3)

for epoch in range(2000):
    pred = model(x)                                # 1. predict
    loss = loss_fn(pred, y)                        # 2. measure error
    optimizer.zero_grad()                          # 3. clear old gradients
    loss.backward()                                # 4. compute gradients
    optimizer.step()                               # 5. update w and b
    if epoch % 400 == 0:
        print(f"epoch {epoch:4d}  loss {loss.item():.5f}")

w = model.weight.item()
b = model.bias.item() * 100
print(f"learned: actual = {w:.2f} * estimate + {b:.1f}")   # about 1.5 and 10

# Predict for a new task: you estimate 40 minutes
with torch.no_grad():
    print("40 min estimate ->", model(torch.tensor([[0.40]])).item() * 100, "min")