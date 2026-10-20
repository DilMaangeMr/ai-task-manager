import torch
from torch import nn
 
# The data: estimates (x) and actual times (y). Divided by 100 only to keep numbers small.
x = torch.tensor([[10.0], [20.0], [30.0], [40.0]]) / 100
y = torch.tensor([[25.0], [40.0], [55.0], [70.0]]) / 100
 
model = nn.Linear(1, 1)                 # the formula: w * x + b (knobs start random)
loss_fn = nn.MSELoss()                  # the score: average of squared misses
optimizer = torch.optim.SGD(model.parameters(), lr=0.5)   # the knob turner
 
for epoch in range(3000):
    pred = model(x)                     # 1. guess
    loss = loss_fn(pred, y)             # 2. score the guesses
    optimizer.zero_grad()               # 3. clear old notes
    loss.backward()                     # 4. find which way to turn each knob
    optimizer.step()                    # 5. turn the knobs a little
    if epoch % 500 == 0:
        print("round", epoch, "loss", round(loss.item(), 6))
 
w = model.weight.item()
b = model.bias.item() * 100             # undo the divide-by-100
print("learned: actual = ", round(w, 2), "x estimate +", round(b, 1))
 
# Use it: predict a task you estimate at 25 minutes
with torch.no_grad():
    print("25 min estimate ->", model(torch.tensor([[0.25]])).item() * 100, "min")
