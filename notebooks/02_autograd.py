import torch

w = torch.tensor(3.0, requires_grad=True)
loss = (2 * w - 10) ** 2           # minimized when w = 5

loss.backward()                     # compute d(loss)/dw
print(w.grad)                       # tensor(-16.)