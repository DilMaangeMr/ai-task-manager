import torch

a = torch.tensor([1.0, 2.0, 3.0])
b = torch.tensor([[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]])

print(a.shape, b.shape)            # torch.Size([3]) torch.Size([3, 2])
print(a * 2)                       # element-wise, no loop needed
print(a + torch.tensor([10.0, 20.0, 30.0]))

# Matrix multiplication: (3,) @ (3, 2) -> (2,)
print(a @ b)

# Reshape and slicing
m = torch.arange(12).reshape(3, 4)
print(m)
print(m[:, 1])                     # second column
print(m.sum(dim=0), m.float().mean())

# Broadcasting: a (3,1) tensor and a (1,4) tensor combine into (3,4)
col = torch.tensor([[1], [2], [3]])
row = torch.tensor([[10, 20, 30, 40]])
print(col + row)

# Types matter
print(a.dtype, m.dtype)            # float32 vs int64