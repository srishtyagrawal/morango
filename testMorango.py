from simulateNode import Node
from syncSession import SyncSession
from storeRecord import StoreRecord 
import unittest

class Test(unittest.TestCase) :

	def test_emptyInstanceID(self) :
		self.assertRaises(ValueError, lambda: Node(""))


	def test_emptyRecordID(self) :
		node = Node("A")
		self.assertRaises(ValueError, lambda: node.addAppData("","data","Facility1","UserX"))

if __name__ == '__main__':
	unittest.main()
