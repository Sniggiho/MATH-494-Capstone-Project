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

            if a == b:
                wMat[a][b] = 0
            else:
                if listOfCourseNumbers[a] == listOfCourseNumbers[b]:
                    wMat[a][b] = 5
                elif key1 in weightsByNum.keys():
                    wMat[a][b] = weightsByNum[key1]

                elif key2 in weightsByNum.keys():
                    wMat[a][b] = weightsByNum[key2]

    return wMat
# -----------------------------------------------------------------------------------------


# -------------------------------- the LP !!???!?!?! ---------------------------------------
profsNumerical = list(range(len(profs)))

allCourses = [135,137,236,237,279,312,365,375,376,377,378,379,432,471,476,477,479] # all courses allowed by our model
courses =    [135,135,135,137,137,137,236,236,237,237,279,279,312,375,377,432] # courses from 2022 fall

coursesNumerical = list(range(len(courses))) # 1 through n, where n=number of courses in supplied schedule
courseMapping = [0,0,0,1,1,1,2,2,3,3,4,4,5,7,8,12] # supplies a mapping from course numbers based on proposed schedule, and course id numbers in the validity matrix
# The id number for the course in the validity matrix is held at the index corresponding to the nuber of the course in the proposed courses


wMat = makeWMat(courses)

intervals = list(range(12))

for p in profsNumerical:
    for a in range(len(allCourses)):
        for i in intervals:
            vMat[p][a][i] = int(vMat[p][a][i])

model = LpProblem(name='classes', sense=LpMinimize)

x = LpVariable.dicts("x", (profsNumerical, coursesNumerical, intervals), cat="Binary")
e = LpVariable.dicts("e", (coursesNumerical, coursesNumerical), lowBound=0)

# CONSTRAINT 1:
for a in coursesNumerical:
    model += lpSum(x[p][a][i] for p in profsNumerical for i in intervals) == 1

# CONSTRAINT 2:
for p in profsNumerical:
    for i in intervals:
        model += lpSum(x[p][a][i] for a in coursesNumerical) <= 1

# CONSTRAINT 3:
for p in profsNumerical:
    for a in coursesNumerical:
        for i in intervals:
            if vMat[p][courseMapping[a]][i] == 0:
                model += (x[p][a][i]==0)

# CONSTRAINT 4:
for p in profsNumerical:
    model += lpSum(x[p][a][i] for a in coursesNumerical for i in intervals) <= 2

# CONSTRAINT 5:
for i in intervals:
    for a in coursesNumerical:
        for b in coursesNumerical[a:]:
            model += (lpSum(x[p][a][i] for p in profsNumerical) +  lpSum(x[p][b][i] for p in profsNumerical) - e[a][b]) <= 1


# CONSTRAINT DAVE:
model += lpSum(x[2][a][i] for a in coursesNumerical for i in intervals) <=1 # Dave only gets to teach one class



# OBJECTIVE FUNCTION: 
obj_func = lpSum(e[a][b]*wMat[a][b] for a in coursesNumerical for b in coursesNumerical)
model += obj_func

status = model.solve(PULP_CBC_CMD(timeLimit=60))

print(f"objective: {model.objective.value()}")



print(f"status: {model.status}, {LpStatus[model.status]}")
# for var in model.variables():
#     if var.value() != 0:
#         print(f"{var.name}: {var.value()}")


for p in profsNumerical:
    for a in coursesNumerical:
        for i in intervals:
            if x[p][a][i].value() == 1:
                print(profs[p],"teaches", courses[a], "in time slot", i)