import copy from deepcopy

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
		self.syncDataStructure = deppcopy(syncDataStructure)

	def updateCounter ( self, increment ) :
		self.counter = self.counter + increment

	def calcFSIC (self, filter ) :
		#Calculate which of the filters are a superset of the filter and insert in list l
		superSetFilters = ["*"]
		fsic = []
		for i in superSetFilters :
			if len(fsic) :
				print "CalcFSIC : Reached here! Needs to be filled!"		
			else :
				fsic = deepcopy(self.syncDataStructure[i])

	def calcDiffFSIC ( self, fsic1, fsic2, filter ) :
	"fsic1 : Local FSIC copy
	 fsic2 : Remote FSIC copy
	 filter : supplied during the initiation of sync session
	 Calculates the maximum counter for every instance ID and updates the local instance's syncDataStructure"
		for key,value in fsic2.items() :
			if fsic1[key] :
				fsic1
			else :
				fsic1[key] = value

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
			
