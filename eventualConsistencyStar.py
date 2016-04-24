from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 

nodeList = []
starSize = 6
for i in range (starSize):
	nodeList.append(Node( chr(i+65) ) )
	# Create 2 records per node 
	nodeList[i].addAppData(chr(i+65) + str(1),chr(i+65) + str(1), Node.ALL, Node.ALL )
	nodeList[i].addAppData(chr(i+65) + str(2),chr(i+65) + str(2), Node.ALL, Node.ALL )
	nodeList[i].serialize((Node.ALL, Node.ALL))

# i client , (starSize -1)  server	
sessIDlist1 = []
#Create sync sessions and store session IDs in a list
for i in range(starSize -1) :
	sessIDlist1.append(nodeList[i].createSyncSession(nodeList[starSize-1], chr(starSize + 64)))
	

for j in range (2) :
	for i in range(starSize-1) :
		# Node i pulling (starSize-1)'s data
		nodeList[i].pullInitiation(sessIDlist1[i], (Node.ALL, Node.ALL)) 
		# Node i pushing data to (starSize-1)
		nodeList[i].pushInitiation(sessIDlist1[i], (Node.ALL, Node.ALL)) 

# Asserts to show that all the nodes have the same data
for i in range(starSize) :
	for j in range (starSize):
		assert nodeList[i].store.has_key(chr(j+65) + "1") == True
		assert nodeList[i].store.has_key(chr(j+65) + "2") == True
