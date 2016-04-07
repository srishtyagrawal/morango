from copy import deepcopy

class Node:
	# Morango instance ID 
	instanceID = None
	# Counter position
	counter = None
	# Sync data structure	
	syncDataStructure = None


	def __init__( self, instanceID, counter, syncDataStructure ):
		"""
		Constructor
		"""
		self.instanceID = instanceID
		self.counter = counter
		self.syncDataStructure = deepcopy(syncDataStructure)


	def updateCounter ( self, increment ) :
		"""
		Update in counter should happen when data is changed at a device
		"""
		self.counter = self.counter + increment


	def convertStrToSet (self, string) :
		"""
		Convert serialized multiple filter representation to set of filters
		"""
		return set(string.split("+"))


	def calcFSIC (self, filter ) :
		"""
		Given a filter(f), finds out maximum counter per instance for all
		filters which are equal to or are superset of filter(f).
		"""
		filterSet = self.convertStrToSet(filter)
		superSetFilters = []
		#Calculate which of the filters are a superset of the filter and insert in list superSetFilters
		for key in self.syncDataStructure.keys():
			keySet = self.convertStrToSet(key)
			if filterSet.issubset(keySet) :
				superSetFilters.append(key)
		fsic = []
		for i in superSetFilters :
			if len(fsic) :
				for k, v in self.syncDataStructure[i].items() :
					# Currently built FSIC contains this instance-counter pair
					if fsic.has_key(k):
						fsic[k] = max(v, fsic[k])
					# Currently built FSIC does not contain this instance-counter pair
					else :
						fsic[k] = v
			# instance-counter pairs being added to FSIC for the first time
			else :
				fsic = deepcopy(self.syncDataStructure[i])
		return fsic

	def updateSyncDS (self, change, filter) :
		"""
		Makes changes to syncDataStructure after data has been received	
		"""
		# Merging existing syncDataSructure to accomodate 
		if self.syncDataStructure.has_key(filter) :
			temp = self.syncDataStructure[filter]
			for key,value in change.items() :
				if temp.has_key(key) :
					temp[key] = value	
				else :
					temp[key] = value
		# no filter exists in the existing syncDataStructure
		else :
			self.syncDataStructure[filter] = change


	def calcDiffFSIC ( self, fsic1, fsic2 ) :
		"""
		fsic1 : Local FSIC copy
		fsic2 : Remote FSIC copy
		Calculates changes, according to the new data which local device has
		"""
		changes = {}
		for key,value in fsic1.items() :
			if fsic2.has_key(key): 
				if fsic2[key] < fsic1[key]:
					changes[key] = fsic1[key]
			else :
				changes[key] = value
		return changes

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
			
