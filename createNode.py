from simulateNode import Node

def pullReq (client, server, filter) :
	clientFSIC = client.calcFSIC(filter)
	#Send filter and clientFSIC to server
	serverFSIC = server.calcFSIC(filter)
	server.calcDiffFSIC(serverFSIC, clientFSIC, filter)
	print "server"
	server.printNode()
	print "client"
	client.printNode()
	

nodeList = []
for i in range (10):
	nodeList.append(Node( i, 0, {}))
	nodeList[i].printNode()

nodeList[0].syncDataStructure = {"*":{"a":10,"b":5,"c":20,"d":45}}
nodeList[1].syncDataStructure = {"*":{"a":12,"b":3,"c":13,"e":50}}

pullReq(nodeList[0], nodeList[1], "*")
