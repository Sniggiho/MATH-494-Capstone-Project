# Rhys and Lola's MATH494 capstone scheduling project
# TODO: Write more up here about the project

from pulp import LpMaximize, LpProblem, LpStatus, LpVariable # LP solver

import csv # csv reading


# --------------------------- import data and create V matrix -----------------------------

profs = ["Alireza", "Andrew", "Kristin", "Lisa", "Lori", "Racheal", "Taryn", "Will"] # the names of each professor to be included in the program

vMat = [None]*len(profs) # initialize the V matrix to be empty

i = 0 # loop variable that numbers the profs

for prof in profs: # reads in each CSV, adding its data to vMat
    currPath = 'V_pai CSVs by Prof\V_' + prof + '.csv'
    with open(currPath, newline = '') as csvfile:
        vMat[i] = list(csv.reader(csvfile))
    i += 1
    
#------------------------------------------------------------------------------------------