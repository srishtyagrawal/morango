from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 

nodeList = []
for i in range (10):
	nodeList.append(Node( chr(i+65) ) )

# Adding a record to a node A
nodeList[0].addAppData("record1","record1", 1, Node.ALL, Node.ALL)
nodeList[0].serialize((Node.ALL, Node.ALL))
assert nodeList[0].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1}}
assert nodeList[0].store["record1"].lastSavedByHistory == {"A":1}

# Adding 2 records to node B 
nodeList[1].addAppData("record2","record2", 1, Node.ALL, Node.ALL)
nodeList[1].addAppData("record3","record3", 1, Node.ALL, Node.ALL)
nodeList[1].serialize((Node.ALL, Node.ALL))
assert nodeList[1].syncDataStructure == {"*+*":{"B":2}}
assert nodeList[1].store["record2"].lastSavedByHistory == {"B":1}
assert nodeList[1].store["record3"].lastSavedByHistory == {"B":2}

#Adding a record to node C
nodeList[2].addAppData("record4","record4", 1, Node.ALL, Node.ALL)
nodeList[2].serialize((Node.ALL, Node.ALL))
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"C":1}}
assert nodeList[2].store["record4"].lastSavedByHistory == {"C":1}

# At this point the nodes have following data :
# A : record1
# B : record2, record3
# C : record4 

# Node A pulling Node B data
sess0_1 = nodeList[0].createSyncSession(nodeList[1], "B")
nodeList[0].pullInitiation(sess0_1, (Node.ALL, Node.ALL))
assert nodeList[0].store["record2"].lastSavedByInstance == "B"
assert nodeList[0].store["record2"].lastSavedByCounter == 1
assert nodeList[0].store["record3"].lastSavedByInstance == "B"
assert nodeList[0].store["record3"].lastSavedByCounter == 2
assert nodeList[0].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1,"B":2}}
assert nodeList[1].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"B":2}}

# Node C pulling Node A data
sess2_0 = nodeList[2].createSyncSession(nodeList[0], "A")
nodeList[2].pullInitiation(sess2_0, (Node.ALL, Node.ALL))
assert nodeList[2].store["record1"].lastSavedByInstance == "A"
assert nodeList[2].store["record1"].lastSavedByCounter == 1
assert nodeList[2].store["record2"].lastSavedByInstance == "B"
assert nodeList[2].store["record2"].lastSavedByCounter == 1
assert nodeList[2].store["record3"].lastSavedByInstance == "B"
assert nodeList[2].store["record3"].lastSavedByCounter == 2
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1,"B":2,"C":1}}

# At this point the nodes have following data :
# A : record1, record2, record3
# B : record2, record3
# C : record1, record2, record3, record4
 
# Adding a record to a node B
nodeList[1].addAppData("record5","record5", 1, Node.ALL, Node.ALL)
nodeList[1].serialize((Node.ALL, Node.ALL))
assert nodeList[1].syncDataStructure == {Node.ALL + "+" + Node.ALL :{"B":3}}
assert nodeList[1].store["record5"].lastSavedByHistory == {"B":3}

# At this point the nodes have following data :
# A : record1, record2, record3
# B : record2, record3, record5
# C : record1, record2, record3, record4 

# Node C pulling Node B data
sess2_1 = nodeList[2].createSyncSession(nodeList[1], "B")
nodeList[2].pullInitiation(sess2_1, (Node.ALL, Node.ALL))
assert nodeList[2].store["record5"].lastSavedByInstance == "B"
assert nodeList[2].store["record5"].lastSavedByCounter == 3
assert nodeList[2].store["record5"].lastSavedByHistory == {"B":3}
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":1}}

# At this point the nodes have following data :
# A : record1, record2, record3
# B : record2, record3, record5
# C : record1, record2, record3, record4, record5 

#Adding a record to node C for Facility1 and *
nodeList[2].addAppData("record6","record6", 1, "Facility1", Node.ALL)
nodeList[2].serialize(("Facility1", Node.ALL))
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL :{"A":1,"B":3,"C":2}}
assert nodeList[2].store["record6"].lastSavedByHistory == {"C":2}

#Adding a record to node C for Facility1 and UserX
nodeList[2].addAppData("record7","record7", 1, "Facility1", "UserX")
nodeList[2].serialize(("Facility1", "UserX"))
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL :{"A":1,"B":3,"C":3}}
assert nodeList[2].store["record7"].lastSavedByHistory == {"C":3}

# At this point the nodes have following data :
# A : record1, record2, record3
# B : record2, record3, record5
# C : record1, record2, record3, record4, record5, record6, record7 

# Node C pushes data to Node A
nodeList[2].pushInitiation(sess2_0, (Node.ALL, Node.ALL))
assert nodeList[2].sessions[sess2_0].serverInstance.instanceID == "A"
assert nodeList[0].sessions[sess2_0].clientInstance.instanceID == "C"
assert nodeList[0].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":3}}
assert nodeList[2].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":3}}

# Node C pushing data to Node B
nodeList[2].pushInitiation(sess2_1, ("Facility1", Node.ALL))
assert nodeList[1].syncDataStructure == {Node.ALL + "+" + Node.ALL:{"B":3}, "Facility1+" + Node.ALL:{"C":3,"A":1}}
