# Rhys and Lola's MATH494 capstone scheduling project
# TODO: Write more up here about the project

from pulp import* # LP solver

import csv # csv reading


# ------------------------------- utilities -----------------------------------------------
def printMat(A): # prints a matrix in a readable fashion
    for row in A:
        print(row)
# -----------------------------------------------------------------------------------------



# --------------------------- import data and create V matrix -----------------------------

profs = ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Lori", "Racheal", "Taryn", "Will"] # the names of each professor to be included in the program

vMat = [None]*len(profs) # initialize the viability matrix to be empty

i = 0 # loop variable that numbers the profs

for prof in profs: # reads in each CSV, adding its data to vMat. Numbers professors in the order they appear in profs
    currPath = 'V_pai CSVs by Prof\V_' + prof + '.csv'
    with open(currPath, newline = '') as csvfile:
        vMat[i] = list(csv.reader(csvfile))
    i += 1
# -----------------------------------------------------------------------------------------


# --------------------------- make conflict weight matrix ---------------------------------
def makeWMat(listOfCourseNumbers):
    weightsByNum = { # this controls how conflicts are weighted based on their course numbers
        100100: 0,
        100200: 2,
        100300: 0,
        100400: 0,
        200200: 3,
        200300: 3,
        200400: 1,
        300300: 4,
        300400: 4,
        400400: 3   
    }

    wMat = [[0 for x in range(len(demoClasses))] for y in range(len(demoClasses))] # initializes the weight matrix with all 0s

    for a in range(len(demoClasses)): # TODO: super inelegant!!! exploit matrix symmetry
        for b in range(len(demoClasses)):
            aLevel = demoClasses[a] - demoClasses[a]%100

            bLevel = demoClasses[b] - demoClasses[b]%100
            key1 = 1000*aLevel + bLevel
            key2 = 1000*bLevel + aLevel


            if key1 in weightsByNum.keys():
                wMat[a][b] = weightsByNum[key1]

            if key2 in weightsByNum.keys():
                wMat[a][b] = weightsByNum[key2]

    return wMat
# -----------------------------------------------------------------------------------------


# -------------------------------- the LP !!???!?!?! ---------------------------------------
courses = [135,137,236,237,279,375,377,479] # a random assortment of courses
profs
intervals = list(range(12))


model = LpProblem(name='classes', sense=LpMinimize)

x = LpVariable.dicts("x", (profs, courses, intervals), cat="Binary")



# x = LpVariable(name="x", lowBound=0, upBound=100)
# y = LpVariable(name="y", lowBound=0, upBound=100)

# model += (x<=95.5)
# model += (y<=94.5)

# obj_func = x + y
# model += obj_func

# status = model.solve()

# print(f"objective: {model.objective.value()}")

# print(f"status: {model.status}, {LpStatus[model.status]}")
# for var in model.variables():
#     print(f"{var.name}: {var.value()}")
