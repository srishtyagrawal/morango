from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 

nodeList = []
for i in range (10):
	nodeList.append(Node( chr(i+65), 0, {}))

# Adding a record to a node A
nodeList[0].addAppData("record1","record1", 1, "*")
nodeList[0].serialize("*")
#nodeList[0].printNode()

# Adding 2 records to node B 
nodeList[1].addAppData("record2","record2", 1, "*")
nodeList[1].addAppData("record3","record3", 1, "*")
nodeList[1].serialize("*")
#nodeList[1].printNode()

#Adding a record to node C
nodeList[2].addAppData("record4","record4", 1, "*")
nodeList[2].serialize("*")


# Node A pulling Node B data
sync0_1 = SyncSession(0, nodeList[0], nodeList[1])
sync0_1.pullInitiation("*")
assert nodeList[0].syncDataStructure == {"*":{"A":1,"B":2}}
#print "printing both node's stores :"
#print nodeList[0].printNode()
#print nodeList[1].printNode()

# Node C pulling Node A data
sync2_0 = SyncSession(1, nodeList[2], nodeList[0])
sync2_0.pullInitiation("*")

# Adding a record to a node B
nodeList[1].addAppData("record5","record5", 1, "*")
nodeList[1].serialize("*")

# Node C pulling Node B data
sync2_1 = SyncSession(2, nodeList[2], nodeList[1])
temp = sync2_1.pullInitiation("*")
