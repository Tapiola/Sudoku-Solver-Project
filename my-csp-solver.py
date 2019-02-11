
import time
import operator
import sys

"""
	The method for handling the file reading.
	Creates the necessary structure for the sudoku table.
	The list of matrices, representing each of them.
"""
def get_sudokus(filename):
	file = open(filename, "r") 
	sudokus_init = file.readlines()
	sudokus = []
	for i in range(len(sudokus_init)):
		table = []
		for x in range(9):
			ls = []
			for y in range(9):
				if sudokus_init[i][x*9+y] == ".":
					ls.append(0)
				else: ls.append(int(sudokus_init[i][x*9+y]))
			table.append(ls)
		sudokus.append(table)
	return sudokus


"""
	Gets the cells that represent the area that cell at x,y could affect.
	Not including the x,y itself.
"""
def getArea(x,y):
	ls = []
	for i in range (9):
		ls.append((i,y))
		ls.append((x,i))
	for i in range (3):
		for j in range (3):
			if not ((x/3)*3+i,(y/3)*3+j) in ls:
				ls.append(((x/3)*3+i,(y/3)*3+j))
	while (x,y) in ls:
		ls.remove((x,y))
	return ls

"""
	Returns all unassigned cells of a given table.
"""
def getUnassigned(table):
	ls = []
	for i in range(9):
		for j in range(9):
			if table[i][j] == 0:
				ls.append((i,j))
	return ls

"""
	Returns all unassigned cells that are in an area.
	The area represents the list of cells some variable x,y could affect.
"""
def getUnssignedArea(unassigned,area):
	count = 0
	for cell in area: 
		if cell in unassigned:
			count += 1
	return count

"""
	Gets the domain of a specific cell x,y.
"""
def getDomain(x,y,table,area):
	domain = [1,2,3,4,5,6,7,8,9]
	for cell in area[x,y]:
		if not table[cell[0]][cell[1]] == 0:
			if table[cell[0]][cell[1]] in domain:
				domain.remove(table[cell[0]][cell[1]])
	# if not table[x][y] == 0:
	# 	if table[x][y] in domain:
	# 		domain.remove(table[x][y])

	return domain

"""
	Gets domains for all cells in the table.
"""
def getDomains(table,area):
	domains = []
	for x in range(9):
		ls = []
		for y in range(9):
			ls.append(getDomain(x,y,table,area))
		domains.append(ls)
	return domains

"""
	Updates all the domains that could be affected
	by writing m into x,y cell/variable.
	Returns the list of all cells that we had to remove m from.
"""
def updateDomains(x,y,m,domains,area):
	ls = []
	for cell in area[x,y]:
		if m in domains[cell[0]][cell[1]]:
			ls.append((cell[0],cell[1]))
			domains[cell[0]][cell[1]].remove(m)
	return ls

"""
	Uses the list returned by update method, which 
	represents the cells that we had to remove m from.
	Adds m back to their domains.
"""
def downdateDomains(x,y,m,domains,ls):
	for cell in ls:
		if not m in domains[cell[0]][cell[1]]:
			domains[cell[0]][cell[1]].append(m)

"""
	Method for mrv heuristic.
"""
def mrv(unassigned, domains):
	dicty = dict()
	for cell in unassigned:
		dicty[(cell[0],cell[1])]=len(domains[cell[0]][cell[1]])
	mrv =  min(dicty, key = dicty.get)
	return mrv


"""
	Forward checking algorithm.
"""
def CSP_FC(table,unassigned,domains,area):
	if len(unassigned) <= 0:
		return table
	# run mrv heuristic and choose variable
	x,y = mrv(unassigned, domains)
	unassigned.remove((x,y))
	for m in domains[x][y]:
		# give x,y cell m meaning temporarily
		table[x][y] = m
		# update domains accordingly
		domain_cache = domains[x][y]
		ls = updateDomains(x,y,m,domains,area)
		domains[x][y] = [m]
		error = False
		# check if one of the domains 
		#in yet unassigned values got empty
		for (i,j) in unassigned:
			if len(domains[i][j]) == 0:
				error = True
				break
		# if they didn't, make recursive step.
		if not error:
			res = CSP_FC(table,unassigned,domains,area)
			if not res == None:
				table = res
				return res
		# backtrack
		# remove m from x,y. make it empty again
		table[x][y] = 0
		# change domains back to how they were
		downdateDomains(x,y,m,domains,ls)
		domains[x][y] = domain_cache
	# put x,y back to unassigned if it's still so
	if not (x,y) in unassigned and table[x][y] == 0:
		unassigned.append((x,y))
	return None


"""
	Main method. Takes care of file reading and file writing.
	Creates all the necessary algorithms.
	Runs the csp algorithm.
"""
def main():
	start_time = time.time()
	reading_file = sys.argv[1]
	sudokus = get_sudokus(reading_file)
	
	writing_file = sys.argv[2]
	file = open(writing_file,"w") 

	area = dict()
	# get area coordinates beforehand
	# since they are the same for all tables
	for i in range(9):
		for j in range(9):
			area[i,j] = getArea(i,j)
	for n in range(len(sudokus)):
		# run fc on each table and solve
		table = sudokus[n]
		domains = getDomains(table,area)
		unassigned = getUnassigned(table)
		CSP_FC(table,unassigned,domains,area)
		# convert list to a string
		# write on file
		st = ""
		for i in range(9):
			for j in range(9):
				st += str(table[i][j])
		st += "\n"
		file.write(st)
	file.close()
	print(time.time() - start_time)
	


if __name__ == "__main__":
    main()

