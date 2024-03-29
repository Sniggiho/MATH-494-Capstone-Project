# Rhys and Lola's MATH494 capstone scheduling project

from pulp import* # LP solver

import csv # csv reading

# --------------------------------------- Global Constants -------------------------------
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
# -----------------------------------------------------------------------------------------

# ------------------------------- general utility------------------------------------------
def printMat(A): # prints a matrix in a readable fashion
    for row in A:
        print(row)
# -----------------------------------------------------------------------------------------


# -------------------------------------  setup helpers ------------------------------------
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
        100200: 2, # 4
        100300: 0, 
        100400: 0,
        200200: 3, # 1
        200300: 3, # 4
        200400: 1, # 2
        300300: 4, # 0
        300400: 4, # 1
        400400: 3 # 0 
    }

    # 4(2) + 3 + 4(3) + 2 + 4 = 29 = Spring 24 dissonance

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

def makeSectionSubsets(courseMapping):
    """Creates the subsets A_k, and stores them at the respective indices of a list
    NOTE: creates subsets with only one course, which must be filtered out later"""
    subsets =  [ [] for _ in range(len(set(courseMapping)))]
    lastVal = courseMapping[0]
    k = 0
    for i in range(len(courseMapping)):
        if courseMapping[i] == lastVal:
            subsets[k].insert(0,i)
        else:
            k += 1
            subsets[k].insert(0,i)
            lastVal = courseMapping[i]

    return subsets
# -----------------------------------------------------------------------------------------


# -------------------------------------- the IP -------------------------------------------
def makeSchedule(profs, courses):
    """Does all preprocessing necessary to run the IP based on the given list of profs and courses. Use this to run schedule creation
    
    NOTE: courses must be sorted in non-decreasing order, and all profs must have corresponding V_[name].csv in 'V_pai CSVs by Prof' folder
    
    ALSO NOTE: constraint Dave is hardcoded to have Dave as professor 2... if that's no longer the case, then constraint dave should be removed/updated"""

    allCourses = [135,137,236,237,279,312,365,375,376,377,378,379,432,471,476,477,479] # all courses allowed by our model

    l = 0
    while courses[l] <300:
        l += 1
        
    wMat = makeWMat(courses)

    profsNumerical = list(range(len(profs)))
    vMat = makeVMat(profs)

    coursesNumerical = list(range(len(courses))) # 1 through n, where n=number of courses in supplied schedule
    courseMapping = makeCourseMapping(allCourses, courses)
    sectionSubsets = makeSectionSubsets(courseMapping)

    intervals = list(range(12))

    courseScheduleIP(profsNumerical, coursesNumerical, courseMapping, intervals, vMat, wMat, courses, profs, l, sectionSubsets)

def courseScheduleIP(profsNumerical, coursesNumerical, courseMapping, intervals, vMat, wMat, courses, profs, l, sectionSubsets):
    """Builds and executes the course scheduling IP, printing out the schedule results, 
    as well as the weight of any conflicts and professor workload violations"""   
    model = LpProblem(name='classes', sense=LpMinimize)

    x = LpVariable.dicts("x", (profsNumerical, coursesNumerical, intervals), cat="Binary")
    e = LpVariable.dicts("e", (coursesNumerical, coursesNumerical), lowBound=0)
    z = LpVariable.dicts("z", (profsNumerical), lowBound=0, upBound=1)
    d = LpVariable.dicts("d", (profsNumerical, coursesNumerical, coursesNumerical, intervals), cat = "Binary")


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

    # # CONSTRAINT 5:
    for p in profsNumerical:
        model += lpSum(x[p][a][i] for a in coursesNumerical[l:] for i in intervals) + z[p] <=2

    # CONSTRAINT 6:
    for p in profsNumerical:
        for a in coursesNumerical:
            for b in coursesNumerical[a+1:]:
                for c in coursesNumerical[b+1:]:
                    m = (courseMapping[b]-courseMapping[a])*(courseMapping[c]-courseMapping[a])*(courseMapping[c]-courseMapping[b])
                    model+= (lpSum(x[p][a][i] for i in intervals) + lpSum(x[p][b][i] for i in intervals) + lpSum(x[p][c][i] for i in intervals))*m <= 2.5*m
    
    # CONSTRAINT 7
    # constraining d:
    for p in profsNumerical:
        for a in coursesNumerical:
            for b in coursesNumerical[a+1:]:
                for i in intervals[:-1]:
                    if a != b:
                        model += (x[p][a][i]+x[p][a][i+1]+x[p][b][i]+x[p][b][i+1] -2*d[p][a][b][i]>= 0)
                        model += (x[p][a][i]+x[p][a][i+1]+x[p][b][i]+x[p][b][i+1] -2*d[p][a][b][i]<= 1)
    # the constraint itself:
    for p in profsNumerical:
        for sectionSet in sectionSubsets:
            if len(sectionSet) > 1:
                model += (lpSum(d[p][sectionSet[b]][sectionSet[a]][i] for a in range(len(sectionSet)) for b in range(a+1,len(sectionSet)) for i in intervals[:-1]) >= lpSum(x[p][a][i] for a in sectionSet for i in intervals) -1 )
    
    
    # CONSTRAINT 8:
    for i in intervals:
        for a in coursesNumerical:
            for b in coursesNumerical[a:]:
                model += (lpSum(x[p][a][i] for p in profsNumerical) +  lpSum(x[p][b][i] for p in profsNumerical) - e[a][b]) <= 1
    
    for a in coursesNumerical:
            for b in coursesNumerical[a:]:
                model += (lpSum(x[p][a][0] for p in profsNumerical) +  lpSum(x[p][b][7] for p in profsNumerical) - e[a][b]) <= 1
                model += (lpSum(x[p][a][7] for p in profsNumerical) +  lpSum(x[p][b][0] for p in profsNumerical) - e[a][b]) <= 1
       
                        
    # CONSTRAINT DAVE:
    model += lpSum(x[2][a][i] for a in coursesNumerical for i in intervals) <=1 # Dave only gets to teach one class


    # OBJECTIVE FUNCTION: 
    weights = lpSum(e[a][b]*wMat[a][b] for a in coursesNumerical for b in coursesNumerical)
    zee = lpSum(z[p] for p in profsNumerical)
    obj_func =  weights + zee
    model += obj_func


    # SOLVE AND PRINT RESULTS
    model.solve(PULP_CBC_CMD(timeLimit=3600))

    print(f"status: {model.status}, {LpStatus[model.status]}")
    print(f"objective: {model.objective.value()}")
    print("Loss from conflicts:", weights.value())
    print("Loss from prof. work load:", zee.value())
    for p in profsNumerical:
        for a in coursesNumerical:
            for i in intervals:
                if x[p][a][i].value() == 1:
                    print(profs[p],"teaches", courseNames[courses[a]], "at", intervalNames[i])
# -----------------------------------------------------------------------------------------


# ------------------------- input to run the program --------------------------------------

profs = ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Lori", "Rachael", "Taryn", "Will"] # the names of each professor to be included in the program
profsFall =  ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Rachael", "Will"] # the names of the profs who taught Fall 2022 (so not Lori or Taryn)
profsSpring = ["Alireza", "Andrew", "David", "Kristin", "Lisa", "Lori", "Rachael", "Will"] # the names of the profs who taught Spring 2022 (so not Taryn)

profsSpring24 = ["Andrew", "David", "Kristin", "Lori", "Taryn", "Will", "Yariana", "Robert", "Paul", "Ben"] # names of the profs who are teaching in spring of '24


coursesFall =    [135,135,135,137,137,137,236,236,237,237,279,279,312,375,377,432, 479] # courses from 2022 fall
coursesSpring =    [135,135,135,137,137,236,236,236,237,237,279,279,312,365,365,376,378,471] # courses from 2023 spring
coursesSpring24 = [135,135,137,137,194,236,236,236,237,279,279,279,312,365,365,376,378,477,479 ] # courses from Spring '24 NOTE: THIS WILL THROW AN ERROR RIGHT NOW AS 194 IS NOT ACCOUNTED FOR


makeSchedule(profsFall, coursesFall)
# ------------------------------------------------------------------------------------------