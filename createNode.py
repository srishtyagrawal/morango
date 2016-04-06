from simulateNode import Node

nodeList = []
for i in range (10):
	nodeList.append(Node( i, 0, {}))
	nodeList[i].printNode()
