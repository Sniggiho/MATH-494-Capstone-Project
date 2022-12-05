# Rhys and Lola's MATH494 capstone scheduling project
# TODO: Write more up here about the project

from pulp import* # LP solver

import csv # csv reading


intervalNames = {
    0: "8:30-9:30 MWF",
    1: "9:40-10:40 MWF",
    2: "10:50-11:50 MWF",
    3: "12:00-1:00 MWF",
    4: "1:10-2:10 MWF",
    5: "2:20-3:20 MWF",
    6: "3:30-4:30 MWF",
    7: "8:00-9:30 MW",
    8: "8:00-9:30 TR",
    9: "9:40-11:10 TR",
    10: "1:20-2:50 TR",
    11: "3:00-4:30 TR",
}

courseNames = {
    135: "135: Calc 1",
    137: "137: Calc 2",
    236: "236: Linear Algebra",
    237: "237: Calc 3",
    279: "279: Discrete",
    312: "312: Diff Eq",
    365: "365: CLA",
    375: "375: Graph Theory",
    376: "376: Alg. Structures",
    377: "377: Real Analysis",
    378: "378: Complex Analysis",
    379: "379: Combinatorics",
    432: "432: Math Modeling",
    471: "471: Topology",
    476: "476: Rep. Theory",
    477: "477: Projects in Analysis",
    479: "479: Network Science",

}


# ------------------------------- utilities -----------------------------------------------
def printMat(A): # prints a matrix in a readable fashion
    for row in A:
        print(row)
# -----------------------------------------------------------------------------------------

# --------------------------- import data and create V matrix -----------------------------
def makeVMat(profs):
    """Takes in a list of professor names, reads the corresponding CSVs, and bakes them into the 3d viability matrix
    
    NOTE: individual professor validity matrices must be in the folder 'V_pai CSVs by Prof', and be named in the form 'V_[prof name].csv'"""

    vMat = [None]*len(profs) # initialize the viability matrix to be empty

    i = 0 # loop variable that numbers the profs

    for prof in profs: # reads in each CSV, adding its data to vMat. Numbers professors in the order they appear in profs
        currPath = 'V_pai CSVs by Prof\V_' + prof + '.csv'
        with open(currPath, newline = '') as csvfile:
            vMat[i] = list(csv.reader(csvfile))
        i += 1

    for p in range(len(vMat)): # converts each entry into an int (rather than a char)
        for a in range(len(vMat[p])):
            for i in range(len(vMat[p][a])):
                vMat[p][a][i] = int(vMat[p][a][i])

    return vMat
# -----------------------------------------------------------------------------------------

# --------------------------- make conflict weight matrix ---------------------------------
def makeWMat(listOfCourseNumbers):
    """
    NOTE: listOfCourseNumbers must be given in numerical non-decreasing order

    Given a list of n three digit macalester course numbers, creates an n x n matrix
    holding the assigned weight of a potential conflict between course i and j in wMat[i][j].
    
    Weights are assigned based on the relative course number of each pair of courses, e.g. 
    a conflict between two 300 level courses is considered quite bad, where a conflict between
    a 100 and 400 level course is not a problem. """

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

    for a in range(len(listOfCourseNumbers)): # uses the above dictionary to fill in the weight matrix
        for b in range(a,len(listOfCourseNumbers)):

            aLevel = listOfCourseNumbers[a] - listOfCourseNumbers[a]%100
            bLevel = listOfCourseNumbers[b] - listOfCourseNumbers[b]%100
            key1 = 1000*aLevel + bLevel

            if a == b: # there is no conflict of a course with itself
                wMat[a][b] = 0
            else:
                if listOfCourseNumbers[a] == listOfCourseNumbers[b]: # if they're different sections of the same course, their conflict should be high
                    wMat[a][b] = 5
                elif key1 in weightsByNum.keys():
                    wMat[a][b] = weightsByNum[key1]

    return wMat
# -----------------------------------------------------------------------------------------

# -------------------------------- the LP !!???!?!?! ---------------------------------------


def makeCourseMapping(allCourses, currentCourses):
    """Makes a list mapping the in-order number of courses in the current selection of courses being sceduled,
    to the number associated with that course in the validity matrix. This becomes important when not all courses
    are offered each term, and some are offered multiple times.
        
    For example, a mapping list like [0,0,0,1,1,1,2,...] indicates that the third course in the current courses
    is course 0 in the validity matrix; in this case because there are three sections of Calc I."""
    courseMapping = [None]*len(currentCourses)

    for i in range(len(currentCourses)):
        courseMapping[i] = allCourses.index(currentCourses[i])

    return courseMapping


def makeSchedule(profs, courses):
    """Does all preprocessing necessary to run the IP based on the given list of profs and courses
    
    TODO: flech this out"""
    allCourses = [135,137,236,237,279,312,365,375,376,377,378,379,432,471,476,477,479] # all courses allowed by our model
    
    wMat = makeWMat(courses)

    profsNumerical = list(range(len(profs)))
    vMat = makeVMat(profs)

    coursesNumerical = list(range(len(courses))) # 1 through n, where n=number of courses in supplied schedule
    courseMapping = makeCourseMapping(allCourses, courses)

    intervals = list(range(12))

    courseScheduleIP(profsNumerical, coursesNumerical, courseMapping, intervals, vMat, wMat, courses, profs)


def courseScheduleIP(profsNumerical, coursesNumerical, courseMapping, intervals, vMat, wMat, courses, profs):
    """The IP itself TODO: flech this out"""   
    model = LpProblem(name='classes', sense=LpMinimize)

    x = LpVariable.dicts("x", (profsNumerical, coursesNumerical, intervals), cat="Binary")
    e = LpVariable.dicts("e", (coursesNumerical, coursesNumerical), lowBound=0)
    z = LpVariable.dicts("e", (profsNumerical), lowBound=0)

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

    # # CONSTRAINT 4:
    for p in profsNumerical:
        model += lpSum(x[p][a][i] for a in coursesNumerical for i in intervals) - z[p] <= 2


    # CONSTRAINT 5:
    for i in intervals:
        for a in coursesNumerical:
            for b in coursesNumerical[a:]:
                model += (lpSum(x[p][a][i] for p in profsNumerical) +  lpSum(x[p][b][i] for p in profsNumerical) - e[a][b]) <= 1


    # CONSTRAINT DAVE:
    model += lpSum(x[2][a][i] for a in coursesNumerical for i in intervals) <=1 # Dave only gets to teach one class TODO: stop hardcoding this!



    # OBJECTIVE FUNCTION: 
    obj_func = lpSum(e[a][b]*wMat[a][b] for a in coursesNumerical for b in coursesNumerical) + lpSum(z[p]for p in profsNumerical)
    model += obj_func


    # SOLVE AND PRINT RESULTS
    model.solve(PULP_CBC_CMD(timeLimit=10))

    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"objective: {model.objective.value()}")
    print(profs)
    for p in profsNumerical:
        for a in coursesNumerical:
            for i in intervals:
                if x[p][a][i].value() == 1:
                    print(profs[p],"teaches", courseNames[courses[a]], "at", intervalNames[i])



profs = ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Lori", "Racheal", "Taryn", "Will"] # the names of each professor to be included in the program
profsFall =  ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Racheal", "Will"] # the names of the profs who taught Fall 2022 (so not Lori or Taryn)

coursesFall =    [135,135,135,137,137,137,236,236,237,237,279,279,312,375,377,432] # courses from 2022 fall
coursesSpring =    [135,135,135,137,137,236,236,236,237,237,279,279,312,365,365,376,378,471] # courses from 2023 spring

makeSchedule(profs, coursesFall)