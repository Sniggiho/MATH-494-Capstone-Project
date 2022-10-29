from pulp import LpMaximize, LpProblem, LpStatus, LpVariable

model = LpProblem(name="test", sense=LpMaximize)

x = LpVariable(name="x", lowBound=0, upBound=100)
y = LpVariable(name="x", lowBound=0, upBound=100)

model += (x<=95)
model += (y<=95)

obj_func = x + y
model += obj_func

status = model.solve()

# print(status)