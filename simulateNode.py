class Node:
	# Morango instance ID 
	instanceID = None
	# Counter position
	counter = None
	# Sync data structure	
	syncDataStructure = None

	def __init__( self, instanceID, counter, syncDataStructure ):
		self.instanceID = instanceID
		self.counter = counter
		# Is this creating a deepcopy?
		self.syncDataStructure = syncDataStructure

	# See if this is a reasonable thing to do! Or do we need to provide the value?
	def updateCounter ( self, increment ) :
		self.counter = self.counter + increment

	#def updateSyncDataStructure ( self ) :

	#def calculateFSIC (self, filterName ) :

	#def calculateDiffFSIC ( fsic1, fsic2 ) :

	def printNode ( self ) :
		"""
		Pretty-printing all the variable values residing in Node object
		"""
		print "Instance ID :" + str(self.instanceID)
		print "Counter value :" + str(self.counter)
		print "syncDataStructure :"
		for key, value in self.syncDataStructure.items() :
			print key + ":"
			print value 
			
