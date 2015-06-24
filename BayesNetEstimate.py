from BayesNetMod import *
import sys

# Checks input for correct length
if len(sys.argv) != 3:
	print "Usage: <BayesNet Structure File> <Data File>"
	sys.exit(0)

# Returns list of nodes in the BayesNet
nodes = parseBayesNet(sys.argv[1])

# Learns CPT tables for Baye Net given a input file
nodes = parseData(sys.argv[2], nodes)

# Prints Baye Net CPT to file
nodesCPTToFile(nodes)
