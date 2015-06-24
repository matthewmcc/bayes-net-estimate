# Used to given floating point for probabilty operations
from __future__ import division

import csv
import math
import sys

# Bayes Net node class
class Node(object):
	# Creates the node
	def __init__(self, name, parents):
		self.name = name
		self.parents = parents
		self.probs = []

		self.value = None
		self.children = []
		# Index of column for node in data
		self.dataIndex = None

	# Returns the conditional probabity of value of the node
	def conditionalProbability(self):

		index = 0;

		# Calculates index of the current prob in the prob list
		for i in range(0, len(self.parents)):
			if self.parents[i].value == "0":
				index += 2 ** (len(self.parents) - i - 1)
		return self.probs[index][1]

	# Sets children list of the node
	def setChildren(self, nodes):
		for node in nodes:
			for nC in nodes:
				for nP in nC.parents:
					if nP == node:
						if nC not in node.children:
							node.children.append(nC)


#### Module of functions for the BayesNetEstimate and BayesNetPredict programs ####

# Changes all nodes parent arrays from string to node pointers.
def linkNodes(nodes):
	for node in nodes:
		for i in range(0, len(node.parents)):
			for n in nodes:
				if node.parents[i] == n.name:
					node.parents[i] = n
					break

# Parser for the Bayes Net File
def parseBayesNet(filename):
	nodes = []
	# Opens file for Net Structure
	try:
		f = open(filename, 'r')
	# Error catch for file not found
	except IOError as (errno, strerror):
		sys.stdout.softspace = 0
		print "I/O error({0}): {1}".format(errno, strerror), ":", fileName
		sys.exit(0)

	# Reads the Baye Net from file
	data = f.readlines()
	for line in data:
		n = line.split()
		nName = n[0]
		nName = nName[:-1]
		n = n[1:]
		nParents = []
		for m in n:
			nParents.append(m)
		nodes.append(Node(nName, nParents))

	linkNodes(nodes)

	return nodes

# Parses the csv data into CPT for each node in BayesNet
def parseData(filename, nodes):
	zero = "0"
	one = "1"

	# Reads in the data from a file
	try:
		with open(filename, 'rb') as f:
			reader = csv.reader(f)
			data = list(reader)

	# Error catch for file not found
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror), ":", filename
		sys.exit(0)

	# Calculate conditional probabilties
	for node in nodes:
		i = data[0].index(node.name)

		# Calculates for nodes with no parents
		if len(node.parents) == 0:
			high, low = 1, 1

			for di in range(1, len(data)):
				if data[di][i] == zero:
					low += 1
				else: high += 1

			node.probs = [[low / (low + high), high / (low + high)]]

		# Calculates for nodes with multiple parents
		else:
			# Index list of parents in datalist
			nindlist = []
			for j in range(0, len(node.parents)):
				nindlist.append(data[0].index(node.parents[j].name))

			# Probibilty tuple list
			p = []
			for pr in range(0, 2 ** len(nindlist)):
				p.append([1, 1])

			# Range for each line in CPT
			for j in range(0, 2 ** len(nindlist)):

				# Bit map for CPT logic
				b = [int(x) for x in bin(j)[2:]]
				for k in range(len(b), len(nindlist)):
					b = [0] + b

				# For all rows of data
				for dInd in range(1, len(data)):

					t = True
					# Test if row that matches CPT logic line
					for k in range(0, len(b)):

						if data[dInd][nindlist[k]] != str(b[k]):
							t = False
							break	

					# If row matches increment probibilty tuple
					if t:
						if data[dInd][i] == one:
							p[j][1] += 1
						else: p[j][0] += 1

				# Calculate probability and append to probs list within node
				node.probs.append([p[j][0] / (p[j][0] + p[j][1]), p[j][1] / (p[j][0] + p[j][1])])
	return nodes

# Writes the bayes net CPT's to file 'output.txt'
def nodesCPTToFile(nodes):
	# Creates the output file
	f = open('output.txt','w')

	for node in nodes:

		# Nodes name
		s = node.name + ":"
		f.write(s)

		# For nodes with no parents
		if len(node.parents) == 0:
			p = '\n' + "0, " + str(node.probs[0][0]) + '\n'
			f.write(p)
			p = "1, " + str(node.probs[0][1]) + '\n'
			f.write(p)

		# For nodes with one or more parents
		else:
			p = ' '
			for np in node.parents:
				p += np.name + " "
			p += '\n'
			f.write(p)

			# Putting CPT in correct for mat then writing to file
			for i in range(0, len(node.probs)):
				b = [int(x) for x in bin(i)[2:]]
				for k in range(len(b), int(math.log(len(node.probs)) / math.log(2))):
					b = [0] + b

				p = ""
				for bit in b:
					p += str(bit)
					p += ", "
				p += str(node.probs[i][1]) + '\n'

				f.write(p)
	f.close

# Uses exact inference to compute the missing values in data
def calculateMissingValues(filename, nodes):
	# Reads in the data from a file
	try:
		with open(filename, 'rb') as f:
			reader = csv.reader(f)
			data = list(reader)

	# Error catch for file not found
	except IOError as (errno, strerror):
		print "I/O error({0}): {1}".format(errno, strerror), ":", filename
		sys.exit(0)

	# Find the index of the missing datas column
	missingIndex = data[1].index("?")

	# Gets index of query node
	queryNode = data[0][missingIndex]
	for n in range(0, len(nodes)):
		if nodes[n].name == queryNode:
			queryNode = n
			break

	# Creates dictionary for node data index and sets their children lists
	nodeIndexs = {}
	for node in nodes:
		index = data[0].index(node.name)
		node.dataIndex = index

		node.setChildren(nodes)


	# Loop for each data row
	for d in range(1, len(data)):

		# Sets bayes net node values for given data in row
		for node in nodes:
			if node.dataIndex != missingIndex:
				node.value = data[d][node.dataIndex]

		# Calculates the markov blanket of the queryNode in the..
		# ...current netwirk state
		if markovsBlankie(queryNode, nodes) < .5:
			data[d][missingIndex] = "0"
		else: data[d][missingIndex] = "1"

	return data

# Writes the data to a csv file 
def csvToFile(data):
	f = open("completedTest.csv", 'wb')
	for datum in data:
		for item in datum:
			f.write(item + ',')
		f.write('\n')

# Computes markov's blankie of the selected queryNode within the 
# nodes bayes net
def markovsBlankie(queryNode, nodes):
	pVector = [0, 0]

	# Calculates the true value of the MB equation 
	nodes[queryNode].value = "0"
	p = nodes[queryNode].conditionalProbability()
	pC = 1

	# Computes the product of childrens CP
	for nC in nodes[queryNode].children:
		if nC.value == "1":
			pC *= nC.conditionalProbability()
		else: pC *= (1 - nC.conditionalProbability())

	pVector[0] = p * pC

	# Calculates the true value of the MB equation 
	nodes[queryNode].value = "1"
	p = nodes[queryNode].conditionalProbability()
	pC = 1

	# Computes the product of childrens CP
	for nC in nodes[queryNode].children:
		if nC.value == "1":
			pC *= nC.conditionalProbability()
		else: pC *= (1 - nC.conditionalProbability())

	pVector[1] = p * pC

	return pVector[0] / (pVector[0] + pVector[1])
