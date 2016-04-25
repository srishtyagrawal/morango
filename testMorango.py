from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 
import unittest
import sys

class Test(unittest.TestCase) :
	RINGSIZE = 6
	STARSIZE = 8

	def test_emptyInstanceID(self) :
		self.assertRaises(ValueError, lambda: Node(""))


	def test_emptyRecordID(self) :
		node = Node("A")
		self.assertRaises(ValueError, lambda: node.addAppData("","data","Facility1","UserX"))

	def test_eventualConsistencyRing(self) :
		nodeList = []
		ringSize = self.RINGSIZE
		print str(ringSize) + " Nodes arranged in ring topology"

		for i in range (ringSize):
        		nodeList.append(Node( chr(i+65) ) )
        		# Create 2 records per node 
        		nodeList[i].addAppData(chr(i+65) + str(1),chr(i+65) + str(1), Node.ALL, Node.ALL )
        		nodeList[i].addAppData(chr(i+65) + str(2),chr(i+65) + str(2), Node.ALL, Node.ALL )
        		nodeList[i].serialize((Node.ALL, Node.ALL))

		# i client , i+1 server 
		sessIDlist = []
		#Create sync sessions and store session IDs in a list
		for i in range(ringSize) :
        		if i == ringSize - 1 :
                		sessIDlist.append(nodeList[i].createSyncSession(nodeList[0], "A"))
        		else :
                		sessIDlist.append(nodeList[i].createSyncSession(nodeList[i+1], chr(i+66)))

		for j in range (2) :
        		for i in range(ringSize) :
                		sessIDlist.append(nodeList[i].createSyncSession(nodeList[0], "A"))
                		# Node i pulling i+1's data
                		nodeList[i].pullInitiation(sessIDlist[i], (Node.ALL, Node.ALL))
                		# Node i pushing data to i+1
                		nodeList[i].pushInitiation(sessIDlist[i], (Node.ALL, Node.ALL))
				
				# Print statements
				if i == ringSize -1 :
					print "Sync data between " + chr(i+65) + " and " + chr(0+65)
				else :
					print "Sync data between " + chr(i+65) + " and " + chr(i+66)

		# Asserts to show that all the nodes have the same data
		for i in range(ringSize) :
        		for j in range (ringSize):
                		self.assertEqual (nodeList[i].store.has_key(chr(j+65) + "1"), True)
                		self.assertEqual (nodeList[i].store.has_key(chr(j+65) + "2"), True)

	def test_eventualConsistencyStar(self) :
		nodeList = []
		starSize = self.STARSIZE
		print str(starSize) + " Nodes arranged in star topology"

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

				# Print statements
				print "Sync data between " + chr(i+65) + " and " + chr(64+starSize)

		# Asserts to show that all the nodes have the same data
		for i in range(starSize) :
        		for j in range (starSize):
                		self.assertEqual (nodeList[i].store.has_key(chr(j+65) + "1"), True)
                		self.assertEqual (nodeList[i].store.has_key(chr(j+65) + "2"), True)


if __name__ == '__main__':
	if len(sys.argv) > 1:
		Test.STARSIZE = int(sys.argv.pop())
		Test.RINGSIZE = int(sys.argv.pop())

	unittest.main()
