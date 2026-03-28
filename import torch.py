import torch
import numpy as np
import matplotlib.pyplot as plt

X_np = np.array([90,100,105,110,115,120,130,133,140]) #Surface
F_np = np.array([3,2,9,3,7,3,6,1,5]) #Floor
P_np = np.array([2.462,2.661,3.177,2.972,3.321,3.226,3.648,3.447,3.848]) #Price

X = torch.from_numpy(X_np.astype(np.float32))
Y = torch.from_numpy(P_np.astype(np.float32))
W = torch.tensor(1.0, dtype = torch.float32, requires_grad = True)

learning_rate = 0.000001
epochs = 100
losses = []

def Model(x):
  return W * x

def Loss(Y_predict, Y):
   return ((Y_predict - Y)**2).sum()
optim = torch.optim.SGD([W], lr=learning_rate)

for epoch in range(epochs):
  Y_predict = Model(X)
  loss  = Loss(Y_predict, Y)
  loss.backward()
  optim.step()
  if epoch % 10 == 0:
    print(f"epoch: {epoch} W: {W} loss: {loss.item():.4f} grad: {W.grad}")
  losses.append(loss.item())
  optim.zero_grad()

plt.figure(figsize=(8,5))
plt.scatter(X_np, P_np, color='blue', label='Data: Price per Surface')
plt.plot(X_np, W.item()*X_np, color='red', label=f'Linear Equation: y={W.item():.4f}*x')
plt.xlabel('Surface')
plt.ylabel('Price')
plt.title('Linear Regression: Apartments')
plt.legend()
plt.grid(True)
plt.show()