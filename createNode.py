from simulateNode import Node

def printServerClientConfig(client, server) : 
	# Print client as well as server configurations 
	print "Server"
	server.printNode()
	print "Client"
	client.printNode()

def pullReq (client, server, filter) :
	"""
	Pull request initialized by client with filter
	"""
	# Step 1 : Client calculates its FSIC locally
	clientFSIC = client.calcFSIC(filter)
	# Step 2 : Client sends filter and its FSIC to server
	# Step 3 : Server creates its FSIC locally
	serverFSIC = server.calcFSIC(filter)
	# Step 4 : Server calculates differences in FSIC
	serverExtra = server.calcDiffFSIC(serverFSIC, clientFSIC)
	# Step 5 : Server sends data to client which abides by serverExtra
	# Step 6 : Client updates its syncDataStructure
	client.updateSyncDS (serverExtra, filter)
	#printServerClientConfig(client, server)

def pushReq (client, server, filter):
	"""
	Push request initialized by client with filter
	"""
	# Step 1 : Client sends Push request along with filter to Server
	# Step 2 : Server caluclates its FSIC and sends it to Client
	serverFSIC = server.calcFSIC(filter)
	# Step 3 : Client creates its own FSIC locally 
	clientFSIC = client.calcFSIC(filter)
	# Step 4 : Client calculates the differences and sees what needs to be pushed
	clientExtra = client.calcDiffFSIC(clientFSIC, serverFSIC)
	# Step 5 : Client sends the data to server according to ClientExtra
	# Step 6 : Server makes changes to its sync Data Structure, after receiving the records 
	server.updateSyncDS( clientExtra, filter)
	#printServerClientConfig(client, server)

nodeList = []
for i in range (10):
	nodeList.append(Node( i, 0, {}))
	#nodeList[i].printNode()


# Testing pull request
nodeList[0].syncDataStructure = {"*":{"a":10,"b":5,"c":20,"d":45}}
nodeList[1].syncDataStructure = {"*":{"a":12,"b":3,"c":13,"e":50}}
pullReq(nodeList[0], nodeList[1], "*")
assert nodeList[0].syncDataStructure == {"*":{"a":12,"b":5,"c":20,"d":45,"e":50}}


# Testing push request
nodeList[0].syncDataStructure = {"*":{"a":9,"b":6,"c":21,"d":46}}
nodeList[1].syncDataStructure = {"*":{"a":11,"b":3,"c":13,"e":52}}
pushReq(nodeList[0], nodeList[1], "*")
assert nodeList[1].syncDataStructure == {"*":{"a":11,"b":6,"c":21,"d":46,"e":52}}

#Testcase where client does not have the filter in its syncDataStructure
nodeList[2].syncDataStructure = {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46},"w":{"g":4}}
nodeList[3].syncDataStructure = {"z+y+w":{"e":2}}
pullReq(nodeList[2], nodeList[3], "y+z")
assert nodeList[2].syncDataStructure == {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46} , "y+z":{"e":2}, "w":{"g":4}}

#Testcase where merging is required as client has pull request filter in its syncDataStructure 
nodeList[2].syncDataStructure = {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46},"w":{"g":4}, "y+z":{"a":5, "e":1}}
nodeList[3].syncDataStructure = {"z+y+w":{"e":2}}
pullReq(nodeList[2], nodeList[3], "y+z")
assert nodeList[2].syncDataStructure == {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46} , "y+z":{"a":5,"e":2}, "w":{"g":4}}
