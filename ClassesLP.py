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

    wMat = [[0 for x in range(len(listOfCourseNumbers))] for y in range(len(listOfCourseNumbers))] # initializes the weight matrix with all 0s

    for a in range(len(listOfCourseNumbers)): # TODO: super inelegant!!! exploit matrix symmetry
        for b in range(len(listOfCourseNumbers)):
            aLevel = listOfCourseNumbers[a] - listOfCourseNumbers[a]%100

            bLevel = listOfCourseNumbers[b] - listOfCourseNumbers[b]%100
            key1 = 1000*aLevel + bLevel
            key2 = 1000*bLevel + aLevel


            if key1 in weightsByNum.keys():
                wMat[a][b] = weightsByNum[key1]

            if key2 in weightsByNum.keys():
                wMat[a][b] = weightsByNum[key2]

    return wMat
# -----------------------------------------------------------------------------------------


# -------------------------------- the LP !!???!?!?! ---------------------------------------
profsNumerical = list(range(len(profs)))

courses = [135,137,236,237,279,375,377,479] # a random assortment of courses
coursesNumerical = list(range(len(courses)))

intervals = list(range(12))



model = LpProblem(name='classes', sense=LpMinimize)

x = LpVariable.dicts("x", (profsNumerical, coursesNumerical, intervals), cat="Binary")


# CONSTRAINT 1:
for a in coursesNumerical:
    model += lpSum(x[p][a][i] for p in profsNumerical for i in intervals) == 1

# CONSTRAINT 2:
for p in profsNumerical:
    for i in intervals:
        model += lpSum(x[p][a][i] for a in coursesNumerical) <= 1

# # CONSTRAINT 3:
# for p in profsNumerical:
#     for a in coursesNumerical:
#         for i in intervals:
#             print(vMat[p][a][i])
#             print(x[p][a][i])

#             model += lpSum(vMat[p][a][i] - x[p][a][i]) >= 0


# CONSTRAINT 4:
for p in profsNumerical:
    model += lpSum(x[p][a][i] for a in coursesNumerical for i in intervals) <= 3



obj_func = 0
model += obj_func

status = model.solve()

print(f"objective: {model.objective.value()}")

print(f"status: {model.status}, {LpStatus[model.status]}")
for var in model.variables():
    print(f"{var.name}: {var.value()}")
