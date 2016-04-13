from simulateNode import Node
from syncSession import SyncSession

nodeList = []
for i in range (10):
	nodeList.append(Node( chr(i+65), 0, {}))

# Adding a record to a node A
nodeList[0].addRecordFromApp("record1","record1")
#nodeList[0].printNode()

# Adding 2 records to node B 
nodeList[1].addRecordFromApp("record2","record2")
nodeList[1].addRecordFromApp("record3","record3")
#nodeList[1].printNode()

# Node A pulling Node B data
sync0_1 = SyncSession(0, nodeList[0], nodeList[1])
sync0_1.pullInitiation("*")
assert nodeList[0].syncDataStructure == {"*":{"A":1,"B":2}}
print "printing both node's stores :"
print nodeList[0].printNode()
print nodeList[1].printNode()
