from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 

nodeList = []
for i in range (10):
	nodeList.append(Node( chr(i+65) ) )

# Adding a record to a node A
nodeList[0].addAppData("record1","record1", 1, "Facility1", "*")
nodeList[0].serialize(("Facility1", "*"))
assert nodeList[0].syncDataStructure == {"*+*":{"A":1}}


