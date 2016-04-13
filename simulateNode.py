from storeRecord import StoreRecord
from copy import deepcopy

class Node:
	# Morango instance ID 
	instanceID = None
	# Counter position
	counter = None
	# Sync data structure	
	syncDataStructure = None
	# Contents of Store
	store = None
	# Contents of Incoming Buffer
	incomingBuffer = None
	# Contents of Outgoing Buffer
	outgoingBuffer = None


	def __init__( self, instanceID, counter, syncDataStructure ):
		"""
		Constructor
		"""
		self.instanceID = instanceID
		self.counter = counter
		# Useful for createNode.py
		#self.syncDataStructure = deepcopy(syncDataStructure)
		# Creating a syncDataStructure with entry for *	
		self.syncDataStructure = {"*":{str(self.instanceID):self.counter}} 
		self.store = {}
		self.incomingBuffer = {}

	def updateCounter ( self ) :
		"""
		Increment counter by 1 when data is saved/modified
		"""
		self.counter = self.counter + 1


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
		fsic = {}
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

	def findRecordInStore ( self, instanceID, counter, partition ) :
		for key, value in self.store.items() :
			#Not included the condition for partition yet
			if value.lastSavedByInstance == instanceID and value.lastSavedByCounter == counter :
				return value 
		return None


	def calcDiffFSIC ( self, fsic1, fsic2 , filter) :
		"""
		fsic1  : Local FSIC copy
		fsic2  : Remote FSIC copy
		filter : filter associated to both FSIC instances
		Calculates changes, according to the new data which local device has
		"""
		records = []
		changes = {}
		for key,value in fsic1.items() :
			if fsic2.has_key(key): 
				if fsic2[key] < fsic1[key]:
					for i in range (fsic2[key], fsic1[key]+1) :
						records.append(self.findRecordInStore(key, i, filter))
					changes[key] = fsic1[key]
			else :
				for i in range (1, value+1):
					records.append(self.findRecordInStore(key, i, filter))
				changes[key] = value
				
		return (changes, records)


	def updateIncomingBuffer (self, pushPullID, filter, records) :
		"""
		Creating Incoming Buffer
		"""
		if self.incomingBuffer.has_key(pushPullID) :
			self.incomingBuffer[str(pushPullID)][1].append(records)
		else :
			self.incomingBuffer[str(pushPullID)] = (filter, records) 


	def addRecordFromApp (self, recordID, recordData) :
		"""
		Adding a new record to the store
		"""
		self.updateCounter()	
		# If store has a record with the same ID
		if self.store.has_key(recordID) :
			temp = self.store[str(recordID)].lastSavedByHistory
			temp[str(self.instanceID)] = self.counter			
			record = StoreRecord(recordID, recordData, self.instanceID, self.counter, temp, "*")
		# Adding a new record with the given recordID
		else :
			record = StoreRecord(recordID, recordData, self.instanceID, self.counter, {str(self.instanceID) : self.counter}, "*")
		self.store[str(recordID)] = record
		# Making changes to Sync Data Structure 
		self.syncDataStructure["*"][str(self.instanceID)] = self.counter

	def integrateRecord (self, record, filter) :
		"""
		Integrate record stored in Incoming Buffer to the store
		"""
		# If record exists in store check for merge-conflicts/fast-forward
		if self.store.has_key(record.recordID) :
			storeRecordHistory = self.store[recordID].lastSavedByHistory
			counter = 0
			# Record's current version exists in storeRecord's history
			if storeRecordHistory.has_key(record.lastSavedByInstance) and storeRecordHistory[record.lastSavedByInstance] > record.lastSavedByCounter :
				counter = counter + 1 
			# storeRecord's current version exists in record's history
			if record.lastSavedByHistory.has_key(self.store[recordID].lastSavedByInstance) and record.lastSavedByHistory[self.store[recordID].lastSavedByInstance] > self.store[recordID].lastSavedByCounter :
				counter = counter + 2
			#TO BE DONE LATER  		
		# Record does not exist in the store, add it
		else :
			self.store[str(record.recordID)] = record


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
		print "Store :"	
		for key, value in self.store.items():
			print key + ":" 
			value.printStoreRecord() 
