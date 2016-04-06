from simulateNode import Node

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
	# Print client as well as server configurations after the exchange 
	print "Server"
	server.printNode()
	print "Client"
	client.printNode()

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
	clientExtra = calcDiffFSIC(clientFSIC, serverFSIC)
	# Step 5 : Client sends the data to server according to ClientExtra
	# Step 6 : Server makes changes to its sync Data Structure, after receiving the records 
	server.updateSyncDS( clientExtra, filter)
	# Print client as well as server configurations after the exchange 
	print "Server"
	server.printNode()
	print "Client"
	client.printNode()

nodeList = []
for i in range (10):
	nodeList.append(Node( i, 0, {}))
	nodeList[i].printNode()

nodeList[0].syncDataStructure = {"*":{"a":10,"b":5,"c":20,"d":45}}
nodeList[1].syncDataStructure = {"*":{"a":12,"b":3,"c":13,"e":50}}
pullReq(nodeList[0], nodeList[1], "*")
assert nodeList[1].syncDataStructure == {"*":{"a":12,"b":5,"c":20,"d":45,"e":50}}

