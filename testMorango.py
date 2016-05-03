from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 
import unittest
import sys
import random

class Test(unittest.TestCase) :
	RINGSIZE = 6
	STARSIZE = 8
	RINGRANDOMSIZE = 5

	def test_emptyInstanceID(self) :
		self.assertRaises(ValueError, lambda: Node(""))


	def test_emptyRecordID(self) :
		self.assertRaises(ValueError, lambda: StoreRecord("","data","A",1,{},"Facility1", "UserX"))


	def test_serialize(self) :
        	node = Node("A")
        	# Create some application data for the node
        	node.addAppData("record1","Record1 data", Node.ALL, Node.ALL )
        	node.addAppData("record2","Record2 data", Node.ALL, Node.GENERIC )
        	node.serialize((Node.ALL, Node.ALL))

		self.assertEqual(len(node.appData), 2)
		# Check if their dirty bits have been cleared 
		self.assertEqual(node.appData[0][2], 0)
		self.assertEqual(node.appData[1][2], 0)

		self.assertEqual(node.store["record1"].lastSavedByInstance, "A")
		self.assertEqual(node.store["record1"].lastSavedByCounter, 1)
		self.assertEqual(node.store["record1"].lastSavedByHistory, {"A":1})
		self.assertEqual(node.store["record1"].partitionFacility, Node.ALL)
		self.assertEqual(node.store["record1"].partitionUser, Node.ALL)

		self.assertEqual(node.store["record2"].lastSavedByInstance, "A")
		self.assertEqual(node.store["record2"].lastSavedByCounter, 2)
		self.assertEqual(node.store["record2"].lastSavedByHistory, {"A":2})
		self.assertEqual(node.store["record2"].partitionFacility, Node.ALL)
		self.assertEqual(node.store["record2"].partitionUser, Node.GENERIC)

		# Create data for different facilities and users
        	node.addAppData("record3","Record3 data", "Facility1", Node.GENERIC )
        	node.addAppData("record4","Record4 data", "Facility1", "UserX" )
        	node.addAppData("record5","Record5 data", "Facility1", "UserY" )
        	node.addAppData("record6","Record6 data", "Facility2", "UserX" )
        	node.addAppData("record7","Record7 data", Node.ALL, Node.ALL)

		self.assertRaises(ValueError, lambda:node.serialize((Node.ALL, "UserX")) )

		node.serialize(("Facility3", "UserZ"))
		# Length of appData nd store should not change after serialization
		self.assertEqual(len(node.store), 2)
		self.assertEqual(len(node.appData), 7)

		node.serialize(("Facility1", "UserX"))
		self.assertEqual(len(node.store), 3)
		self.assertEqual(len(node.appData), 7)
		self.assertEqual(node.appData[3][2], 0)
		self.assertEqual(node.store["record4"].lastSavedByInstance, "A")
		self.assertEqual(node.store["record4"].lastSavedByCounter, 3)
		self.assertEqual(node.store["record4"].lastSavedByHistory, {"A":3})
		self.assertEqual(node.store["record4"].partitionFacility, "Facility1")
		self.assertEqual(node.store["record4"].partitionUser, "UserX")

		node.serialize(("Facility1", Node.ALL))
		self.assertEqual(len(node.store), 5)
		self.assertEqual(len(node.appData), 7)
		self.assertEqual(node.appData[2][2], 0)
		self.assertEqual(node.appData[4][2], 0)
		self.assertEqual(node.store["record3"].lastSavedByHistory, {"A":4})
		self.assertEqual(node.store["record5"].lastSavedByHistory, {"A":5})

		node.serialize((Node.ALL, Node.ALL))
		self.assertEqual(len(node.store), 7)
		self.assertEqual(len(node.appData), 7)
		self.assertEqual(node.appData[5][2], 0)
		self.assertEqual(node.appData[6][2], 0)
		self.assertEqual(node.store["record6"].lastSavedByHistory, {"A":6})
		self.assertEqual(node.store["record7"].lastSavedByHistory, {"A":7})


	def test_compareVectors(self) :
        	n = Node("A")
		self.assertEqual(n.compareVectors({"A":1},{"A":2}), 0)
		self.assertEqual(n.compareVectors({"A":1},{"A":1, "B":2}), 0)
		self.assertEqual(n.compareVectors({"A":4, "B":3},{"A":2}), 1)
		self.assertEqual(n.compareVectors({"A":2, "B":3},{"A":2}), 1)
		self.assertEqual(n.compareVectors({"A":2, "B":3},{"A":3}), 2)


	def createNodes(self, size):
		"""
		Creates size number of nodes and puts it in a list.
		"""
		nodeList = []
		for i in range(size) :
			nodeList.append(Node(chr(i+65)))
		return nodeList

	def addAppRecordMerge (self, nodeList) :
		"""
		Adds an application record to each node in the nodeList such that
		they create a merge conflict among each other. i.e their IDs are same but 
		different data.
		"""
		for i in range(len(nodeList)) :
			nodeList[i].addAppData("id","data " + chr(i+65) , Node.ALL, Node.ALL)
			nodeList[i].serialize((Node.ALL, Node.ALL))


	def addAppRecordDiff (self, nodeList) :
		"""
		Adds an application record to each node in the nodelist such that they have different recordIDs
		"""
		for i in range(len(nodeList)) :
			nodeList[i].addAppData("record" + chr(i+65) , "recordData"+ chr(i+65), Node.ALL, Node.ALL)
			nodeList[i].serialize((Node.ALL, Node.ALL))


	def test_scenario1(self) :
		nodeList = self.createNodes(3)

		# Adding a record to a node A
		nodeList[0].addAppData("record1","record1", Node.ALL, Node.ALL)
		nodeList[0].serialize((Node.ALL, Node.ALL))
		self.assertEqual(nodeList[0].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1}})
		self.assertEqual(nodeList[0].store["record1"].lastSavedByHistory, {"A":1})

		# Adding 2 records to node B 
		nodeList[1].addAppData("record2","record2", Node.ALL, Node.ALL)
		nodeList[1].addAppData("record3","record3", Node.ALL, Node.ALL)
		nodeList[1].serialize((Node.ALL, Node.ALL))
		self.assertEqual(nodeList[1].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"B":2}})
		self.assertEqual(nodeList[1].store["record2"].lastSavedByHistory, {"B":1})
		self.assertEqual(nodeList[1].store["record3"].lastSavedByHistory, {"B":2})

		#Adding a record to node C
		nodeList[2].addAppData("record4","record4", Node.ALL, Node.ALL)
		nodeList[2].serialize((Node.ALL, Node.ALL))
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"C":1}})
		self.assertEqual(nodeList[2].store["record4"].lastSavedByHistory, {"C":1})

		# At this point the nodes have following data :
		# A : record1
		# B : record2, record3
		# C : record4 

		# Node A pulling Node B data
		sess0_1 = nodeList[0].createSyncSession(nodeList[1], "B")
		nodeList[0].pullInitiation(sess0_1, (Node.ALL, Node.ALL))
		self.assertEqual(nodeList[0].store["record2"].lastSavedByInstance, "B")
		self.assertEqual(nodeList[0].store["record2"].lastSavedByCounter, 1)
		self.assertEqual(nodeList[0].store["record3"].lastSavedByInstance, "B")
		self.assertEqual(nodeList[0].store["record3"].lastSavedByCounter, 2)
		self.assertEqual(nodeList[0].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1,"B":2}})
		self.assertEqual(nodeList[1].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"B":2}})

		# Node C pulling Node A data
		sess2_0 = nodeList[2].createSyncSession(nodeList[0], "A")
		nodeList[2].pullInitiation(sess2_0, (Node.ALL, Node.ALL))
		self.assertEqual(nodeList[2].store["record1"].lastSavedByInstance, "A")
		self.assertEqual(nodeList[2].store["record1"].lastSavedByCounter, 1)
		self.assertEqual(nodeList[2].store["record2"].lastSavedByInstance, "B")
		self.assertEqual(nodeList[2].store["record2"].lastSavedByCounter, 1)
		self.assertEqual(nodeList[2].store["record3"].lastSavedByInstance, "B")
		self.assertEqual(nodeList[2].store["record3"].lastSavedByCounter, 2)
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1,"B":2,"C":1}})

		# At this point the nodes have following data :
		# A : record1, record2, record3
		# B : record2, record3
		# C : record1, record2, record3, record4

		# Adding a record to a node B
		nodeList[1].addAppData("record5","record5", Node.ALL, Node.ALL)
		nodeList[1].serialize((Node.ALL, Node.ALL))
		self.assertEqual(nodeList[1].syncDataStructure, {Node.ALL + "+" + Node.ALL :{"B":3}})
		self.assertEqual(nodeList[1].store["record5"].lastSavedByHistory, {"B":3})

		# At this point the nodes have following data :
		# A : record1, record2, record3
		# B : record2, record3, record5
		# C : record1, record2, record3, record4 

		# Node C pulling Node B data
		sess2_1 = nodeList[2].createSyncSession(nodeList[1], "B")
		nodeList[2].pullInitiation(sess2_1, (Node.ALL, Node.ALL))
		self.assertEqual(nodeList[2].store["record5"].lastSavedByInstance, "B")
		self.assertEqual(nodeList[2].store["record5"].lastSavedByCounter, 3)
		self.assertEqual(nodeList[2].store["record5"].lastSavedByHistory, {"B":3})
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":1}})

		# At this point the nodes have following data :
		# A : record1, record2, record3
		# B : record2, record3, record5
		# C : record1, record2, record3, record4, record5 

		#Adding a record to node C for Facility1 and Node.GENERIC
		nodeList[2].addAppData("record6","record6", "Facility1", Node.GENERIC)
		nodeList[2].serialize(("Facility1", Node.ALL))
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL :{"A":1,"B":3,"C":2}})
		self.assertEqual(nodeList[2].store["record6"].lastSavedByHistory, {"C":2})

		#Adding a record to node C for Facility1 and UserX
		nodeList[2].addAppData("record7","record7", "Facility1", "UserX")
		nodeList[2].serialize(("Facility1", "UserX"))
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL :{"A":1,"B":3,"C":3}})
		self.assertEqual(nodeList[2].store["record7"].lastSavedByHistory, {"C":3})

		# At this point the nodes have following data :
		# A : record1, record2, record3
		# B : record2, record3, record5
		# C : record1, record2, record3, record4, record5, record6, record7 

		# Node C pushes data to Node A
		nodeList[2].pushInitiation(sess2_0, (Node.ALL, Node.ALL))
		self.assertEqual(nodeList[2].sessions[sess2_0].serverInstance.instanceID, "A")
		self.assertEqual(nodeList[0].sessions[sess2_0].clientInstance.instanceID, "C")
		self.assertEqual(nodeList[0].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":3}})
		self.assertEqual(nodeList[2].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"A":1,"B":3,"C":3}})

		# At this point the nodes have following data :
		# A : record1, record2, record3, record4, record5, record6, record7
		# B : record2, record3, record5
		# C : record1, record2, record3, record4, record5, record6, record7 

		# Node C pushing data to Node B
		nodeList[2].pushInitiation(sess2_1, ("Facility1", Node.ALL))
		self.assertEqual(nodeList[1].syncDataStructure, {Node.ALL + "+" + Node.ALL:{"B":3}, "Facility1+" + Node.ALL:{"C":3,"A":1}})

		# At this point the nodes have following data :
		# A : record1, record2, record3, record4, record5, record6, record7
		# B : record2, record3, record5, record6, record7
		# C : record1, record2, record3, record4, record5, record6, record7 


	def test_fast_forward_scenario1 (self) :
		m = self.createNodes(3)

		# Adding a record to a node A
		m[0].addAppData("record1","A version 1", Node.ALL, Node.ALL)
		m[0].serialize((Node.ALL, Node.ALL))
		
		# Node A pushing data to Node B
		sess0_1 = m[0].createSyncSession(m[1], "B")
		m[0].pushInitiation(sess0_1, (Node.ALL, Node.ALL))
		self.assertEqual(m[1].store["record1"].lastSavedByInstance, "A")
		self.assertEqual(m[1].store["record1"].lastSavedByCounter, 1)
		self.assertEqual(m[1].store["record1"].lastSavedByHistory, {"A":1})
		self.assertEqual(m[1].store["record1"].partitionFacility, Node.ALL)
		self.assertEqual(m[1].store["record1"].partitionUser, Node.ALL)
		self.assertEqual(m[1].store["record1"].recordData, "A version 1")

		recordIndex = m[1].searchRecordInApp("record1")	
		self.assertEqual(m[1].appData[recordIndex][1], "A version 1")
		self.assertEqual(m[1].appData[recordIndex][2], 0)
		self.assertEqual(m[1].appData[recordIndex][3], Node.ALL)
		self.assertEqual(m[1].appData[recordIndex][4], Node.ALL)

		# Node B now modifies this data
		m[1].addAppData("record1","B version 1", Node.ALL, Node.ALL)
		self.assertEqual(m[1].appData[recordIndex][1], "B version 1")
		self.assertEqual(m[1].appData[recordIndex][2], 1)

		m[1].serialize((Node.ALL, Node.ALL))
		self.assertEqual(m[1].appData[recordIndex][2], 0)
		self.assertEqual(m[1].store["record1"].lastSavedByInstance, "B")
		self.assertEqual(m[1].store["record1"].lastSavedByCounter, 1)
		self.assertEqual(m[1].store["record1"].lastSavedByHistory, {"A":1, "B":1})
		self.assertEqual(m[1].store["record1"].partitionFacility, Node.ALL)
		self.assertEqual(m[1].store["record1"].partitionUser, Node.ALL)
		self.assertEqual(m[1].store["record1"].recordData, "B version 1")

		# Node B pushing data to Node C
		sess1_2 = m[1].createSyncSession(m[2], "C")
		m[1].pushInitiation(sess1_2, (Node.ALL, Node.ALL))
		self.assertEqual(m[2].store["record1"].lastSavedByInstance, "B")
		self.assertEqual(m[2].store["record1"].lastSavedByCounter, 1)
		self.assertEqual(m[2].store["record1"].lastSavedByHistory, {"A":1, "B":1})
		self.assertEqual(m[2].store["record1"].partitionFacility, Node.ALL)
		self.assertEqual(m[2].store["record1"].partitionUser, Node.ALL)
		self.assertEqual(m[2].store["record1"].recordData, "B version 1")

		# Node A pushing data to Node C
		sess0_2 = m[0].createSyncSession(m[2], "C")
		m[0].pushInitiation(sess0_2, (Node.ALL, Node.ALL))
		self.assertEqual(m[2].store["record1"].lastSavedByInstance, "B")
		self.assertEqual(m[2].store["record1"].lastSavedByCounter, 1)
		self.assertEqual(m[2].store["record1"].lastSavedByHistory, {"A":1, "B":1})
		self.assertEqual(m[2].store["record1"].partitionFacility, Node.ALL)
		self.assertEqual(m[2].store["record1"].partitionUser, Node.ALL)
		self.assertEqual(m[2].store["record1"].recordData, "B version 1")


	def test_mergeConflict_scenario1(self) :
		p = self.createNodes(4)

		# Adding a record to a node A
		p[0].addAppData("record1","A version 1", Node.ALL, Node.ALL)
		p[0].serialize((Node.ALL, Node.ALL))
		self.assertEqual(p[0].store["record1"].lastSavedByHistory, {"A":1})
		
		# Adding a record to a node B
		p[1].addAppData("record1","B version 1", Node.ALL, Node.ALL)
		p[1].serialize((Node.ALL, Node.ALL))
		self.assertEqual(p[1].store["record1"].lastSavedByHistory, {"B":1})

		# Node A pushing data to Node C
		sess0_2 = p[0].createSyncSession(p[2], "C")
		p[0].pushInitiation(sess0_2, (Node.ALL, Node.ALL))
		self.assertEqual(p[2].store["record1"].lastSavedByHistory, {"A":1})

		# Node B pushing data to Node C
		sess1_2 = p[1].createSyncSession(p[2], "C")
		p[1].pushInitiation(sess1_2, (Node.ALL, Node.ALL))
		self.assertEqual(p[2].store["record1"].lastSavedByHistory, {"A":1,"B":1,"C":1})


		# Node B pushing data to Node D
		sess1_3 = p[1].createSyncSession(p[3], "D")
		p[1].pushInitiation(sess1_3, (Node.ALL, Node.ALL))
		self.assertEqual(p[3].store["record1"].lastSavedByHistory, {"B":1})

		# Node A pushing data to Node D
		sess0_3 = p[0].createSyncSession(p[3], "D")
		p[0].pushInitiation(sess0_3, (Node.ALL, Node.ALL))
		self.assertEqual(p[3].store["record1"].lastSavedByInstance, "D")
		self.assertEqual(p[3].store["record1"].lastSavedByHistory, {"B":1, "A":1, "D":1})
		self.assertEqual(p[2].store["record1"].recordData, p[3].store["record1"].recordData)

		# Node C pushing data to Node D
		sess2_3 = p[2].createSyncSession(p[3], "D")
		p[2].pushInitiation(sess2_3, (Node.ALL, Node.ALL))
		self.assertEqual(p[3].store["record1"].lastSavedByHistory, {"B":1, "A":1, "D":2, "C":1})

		# Node C pulling data from Node D
		p[2].pullInitiation(sess2_3, (Node.ALL, Node.ALL))
		self.assertEqual(p[2].store["record1"].lastSavedByHistory, {"B":1, "A":1, "D":2, "C":1})


	def endConditionData (self, nodeList) :
		data  = set([])
		for i in range (len(nodeList)) :
			for k,v in nodeList[i].store.items():
				data.add(v.recordID)

		for i in range(len(nodeList)) :
			if len(nodeList[i].store) != len(data) :
				return True
			else :
				for m in data :
					if not(nodeList[i].store.has_key(m)) :
						return True
					
		return False


	def endConditionMerge (self, nodeList) :
		data = nodeList[0].store["id"].lastSavedByHistory
		for i in range(1, len(nodeList)) :
			if nodeList[i].store["id"].lastSavedByHistory != data :
				return True
		return False


	def fullDBReplication(self, clientHandler, sessionID ):
                # Client pulling server's data
                clientHandler.pullInitiation(sessionID, (Node.ALL, Node.ALL))
                # Client pushing data to server
                clientHandler.pushInitiation(sessionID, (Node.ALL, Node.ALL))


	def sessionsRing(self, nodeList) :
		sessIDlist = []
		#Create sync sessions and store session IDs in a list
		ringSize = len(nodeList)
		for i in range(ringSize) :
        		if i == ringSize - 1 :
                		sessIDlist.append((i, 0, nodeList[i].createSyncSession(nodeList[0], "A")))
        		else :
                		sessIDlist.append((i, i+1, nodeList[i].createSyncSession(nodeList[i+1], chr(i+66))))
		return sessIDlist


	def test_eventualConsistencyRing(self) :
		ringSize = self.RINGSIZE
		print str(ringSize) + " Nodes arranged in ring topology"

		nodeList = self.createNodes(ringSize)
		self.addAppRecordDiff(nodeList)

		# i client , i+1 server 
		sessIDlist = self.sessionsRing(nodeList)

		for j in range (2) :
        		for i in range(ringSize) :
                		sessIDlist.append(nodeList[i].createSyncSession(nodeList[0], "A"))
				self.fullDBReplication(nodeList[sessIDlist[i][0]], sessIDlist[i][2])
				
				# Print statements
				if i == ringSize -1 :
					print "Sync data between " + chr(i+65) + " and " + chr(0+65)
				else :
					print "Sync data between " + chr(i+65) + " and " + chr(i+66)

		# Asserts to show that all the nodes have the same data
		self.assertEqual(self.endConditionData(nodeList) , False)


	def test_eventualConsistencyStar(self) :
		starSize = self.STARSIZE
		print str(starSize) + " Nodes arranged in star topology"

		nodeList = self.createNodes(starSize)
		self.addAppRecordDiff(nodeList)

		# i client , (starSize -1)  server      
		sessIDlist1 = []
		#Create sync sessions and store session IDs in a list
		for i in range(starSize -1) :
        		sessIDlist1.append(nodeList[i].createSyncSession(nodeList[starSize-1], chr(starSize + 64)))


		for j in range (2) :
        		for i in range(starSize-1) :
				self.fullDBReplication(nodeList[i], sessIDlist1[i])

				# Print statements
				print "Sync data between " + chr(i+65) + " and " + chr(64+starSize)

		# Asserts to show that all the nodes have the same data
		self.assertEqual(self.endConditionData(nodeList) , False)


	def test_eventualRingRandom (self) :
		nextExchange = []
		ringSize = self.RINGRANDOMSIZE
		nodeList = self.createNodes(ringSize)
		self.addAppRecordMerge(nodeList)
		sessionInfo = self.sessionsRing(nodeList)

		loop = 0 
		while self.endConditionMerge(nodeList) :
			nextExchange = [x for x in range(ringSize)]
			while len(nextExchange) > 0 :
				index = random.randint(0, len(nextExchange)-1)
				sess = sessionInfo[nextExchange[index]]
				# Full DB replication 
				self.fullDBReplication(nodeList[sess[0]], sess[2])
				self.assertEqual(nodeList[sess[0]].store["id"].lastSavedByHistory, nodeList[sess[1]].store["id"].lastSavedByHistory)
				del nextExchange[index]
			loop = loop + 1			
		print loop
		self.assertLessEqual(loop, ringSize * ringSize)


	def eventualFullConnectedRandom (self, networkSize) :
		nodeList = self.createNodes(networkSize)
		self.addAppRecordMerge(nodeList)
		sessionInfo = []

		for i in range (networkSize) :
			for j in range(networkSize):
				if(i != j) :
					sessionInfo.append((i,j, (nodeList[i].createSyncSession(nodeList[j], chr(j+65)))))

		total = 0 
		while self.endConditionMerge(nodeList) :
			index = random.randint(0, len(sessionInfo)-1)
			nodeList[sessionInfo[index][0]].pullInitiation(sessionInfo[index][2],\
				 (Node.ALL, Node.ALL))	
			total = total + 1			
		return total


	def test_multipleEventualFull (self) :
		temp = []
		f = open("mergeStats", "a+")

		for j in range(3,10) :
			for i in range(10) :
				temp.append(self.eventualFullConnectedRandom(j))
			f.write(str(j))
			f.write("\n")
			f.write(str(temp))	
			f.write("\n")
			del temp[:]
		
if __name__ == '__main__':
	if len(sys.argv) > 1:
		Test.STARSIZE = int(sys.argv.pop())
		Test.RINGSIZE = int(sys.argv.pop())
		Test.RINGRANDOMSIZE = int(sys.argv.pop())
	unittest.main()
