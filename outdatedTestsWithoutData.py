from simulateNode import Node
from syncSession import SyncSession

nodeList = []
for i in range (10):
	nodeList.append(Node( chr(i+65) ))

# Testing pull request
nodeList[0].syncDataStructure = {"*+*":{"a":10,"b":5,"c":20,"d":45}}
nodeList[1].syncDataStructure = {"*+*":{"a":12,"b":3,"c":13,"e":50}}
sync0_1 = SyncSession(0, nodeList[0], nodeList[1])
sync0_1.pullInitiation("*+*")
assert nodeList[0].syncDataStructure == {"*+*":{"a":12,"b":5,"c":20,"d":45,"e":50}}

# Testing push request
nodeList[0].syncDataStructure = {"*":{"a":9,"b":6,"c":21,"d":46}}
nodeList[1].syncDataStructure = {"*":{"a":11,"b":3,"c":13,"e":52}}
sync0_1 = SyncSession(1, nodeList[0], nodeList[1])
sync0_1.pushInitiation("*")
assert nodeList[1].syncDataStructure == {"*":{"a":11,"b":6,"c":21,"d":46,"e":52}}

#Testcase where client does not have the filter in its syncDataStructure
nodeList[2].syncDataStructure = {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46},"w":{"g":4}}
nodeList[3].syncDataStructure = {"z+y+w":{"e":2}}
sync2_3 = SyncSession(0, nodeList[2], nodeList[3])
sync2_3.pullInitiation("y+z")
assert nodeList[2].syncDataStructure == {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46} , "y+z":{"e":2}, "w":{"g":4}}

#Testcase where merging is required as client has pull request filter in its syncDataStructure 
nodeList[2].syncDataStructure = {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46},"w":{"g":4}, "y+z":{"a":5, "e":1}}
nodeList[3].syncDataStructure = {"z+y+w":{"e":2}}
sync2_3 = SyncSession(1, nodeList[2], nodeList[3])
sync2_3.pullInitiation("y+z")
assert nodeList[2].syncDataStructure == {"x":{"a":9,"b":6,"c":21,"d":46},"x+y":{"a":46} , "y+z":{"a":5,"e":2}, "w":{"g":4}}

#Adding a record to a node
nodeList[4].addRecordFromApp("record1","abcd")
nodeList[4].printNode()
