import numpy as np

a = np.array([1, 2, 3, 4, 5])
b = [a]
b.append([])
print(a*a)
print(b)

for i in b:
    print("懶蛋")