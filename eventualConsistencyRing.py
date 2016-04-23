from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 

nodeList = []
ringSize = 10
for i in range (ringSize):
	nodeList.append(Node( chr(i+65) ) )
	# Create 2 records per node 
	nodeList[i].addAppData(chr(i+65) + str(1),chr(i+65) + str(1),1, Node.ALL, Node.ALL )
	nodeList[i].addAppData(chr(i+65) + str(2),chr(i+65) + str(2),1, Node.ALL, Node.ALL )
	nodeList[i].serialize((Node.ALL, Node.ALL))

# i client , i+1 server	
sessIDlist1 = []
#Create sync sessions and store session IDs in a list
for i in range(ringSize) :
	if i == ringSize - 1 :
		sessIDlist1.append(nodeList[i].createSyncSession(nodeList[0], "A"))
	else :
		sessIDlist1.append(nodeList[i].createSyncSession(nodeList[i+1], chr(i+66)))
	

for j in range (2) :
	for i in range(ringSize) :
		# Node i pulling i+1's data
		nodeList[i].pullInitiation(sessIDlist1[i], (Node.ALL, Node.ALL)) 
		# Node i pushing data to i+1
		nodeList[i].pushInitiation(sessIDlist1[i], (Node.ALL, Node.ALL)) 

# Asserts to show that all the nodes have the same data
for i in range(ringSize) :
	for j in range (ringSize):
		assert nodeList[i].store.has_key(chr(j+65) + "1") == True
		assert nodeList[i].store.has_key(chr(j+65) + "2") == True
