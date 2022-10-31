from pulp import LpMaximize, LpProblem, LpStatus, LpVariable

model = LpProblem(name='test', sense=LpMaximize)

x = LpVariable(name="x", lowBound=0, upBound=100)
y = LpVariable(name="y", lowBound=0, upBound=100)

model += (x<=95)
model += (y<=95)

obj_func = x + y
model += obj_func

status = model.solve()

print(f"status: {model.status}, {LpStatus[model.status]}")
print(f"objective: {model.objective.value()}")
for var in model.variables():
    print(f"{var.name}: {var.value()}")