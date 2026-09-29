import interp1d

x = [ 1, 5, 17]  # Inputs
y = [20, 6, 14]  # Outputs
mapping = interp1d.Linear(x, y)
print(mapping(11))  # 10.0
