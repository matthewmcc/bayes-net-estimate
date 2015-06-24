from BayesNetMod import *
import sys

# Checks input for correct length
if len(sys.argv) != 4:
	print "Usage: <BayesNet Structure File> <Training Data File> <Test Data File"
	sys.exit(0)

# Returns list of nodes in the BayesNet
nodes = parseBayesNet(sys.argv[1])

# Learns CPT tables for Baye Net given a input file
nodes = parseData(sys.argv[2], nodes)

# Predicts the spam value for the test data.
data = calculateMissingValues(sys.argv[3], nodes)

# Output data with predicted values to a test file.
csvToFile(data)