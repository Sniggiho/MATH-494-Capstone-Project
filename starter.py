from pulp import*

# model = LpProblem(name='test', sense=LpMaximize)

# x = LpVariable(name="x", lowBound=0, upBound=100)
# y = LpVariable(name="y", lowBound=0, upBound=100)

# model += (x<=95)
# model += (y<=95)

# obj_func = x + y
# model += obj_func

# status = model.solve()

# print(f"status: {model.status}, {LpStatus[model.status]}")
# print(f"objective: {model.objective.value()}")
# for var in model.variables():
#     print(f"{var.name}: {var.value()}")


model = LpProblem(name='classes', sense=LpMaximize)

dummy = ['a','b']
dummy2 = [1,2,3]
dummy3 = [135,237]

x = LpVariable.dicts("x", (dummy, dummy2, dummy3), lowBound=10, upBound=100)

# x = LpVariable(name="x", lowBound=0, upBound=100)
# y = LpVariable(name="y", lowBound=0, upBound=100)


# sum of x_a_i == 90 over i for all a

for c in dummy:
    model += lpSum(x[c][i][num] for i in dummy2 for num in dummy3) == 90



obj_func = x['a'][1][135] + x['b'][2][237] + x['b'][1][135] +x['a'][2][237]
model += obj_func

status = model.solve()

print(f"objective: {model.objective.value()}")

print(f"status: {model.status}, {LpStatus[model.status]}")
for var in model.variables():
    print(f"{var.name}: {var.value()}")