from storeRecord import StoreRecord
from copy import deepcopy

class Node:
	# Morango instance ID 
	instanceID = None
	# Morango Counter position
	counter = None
	# Sync data structure	
	syncDataStructure = None
	# Contents of Store
	store = None
	# Contents of Incoming Buffer
	incomingBuffer = None
	# Contents of Outgoing Buffer
	outgoingBuffer = None
	# Imitation of application data
	appData = None
	# Pending requests queue
	requests = None

	def __init__( self, instanceID):
		"""
		Constructor
		"""
		self.instanceID = instanceID
		self.counter = 0
		self.syncDataStructure = {"*+*":{str(self.instanceID):self.counter}} 
		self.store = {}
		self.incomingBuffer = {}
		self.appData = []
		self.outgoingBuffer = {}
		self.requests = []


	def updateCounter ( self ) :
		"""
		Increment counter by 1 when data is saved/modified
		"""
		self.counter = self.counter + 1


	def addAppData ( self, recordID, recordData, dirtyBit, partitionFacility, partitionUser) :
		"""
		Adding records to the application
		"""
		self.appData.append((recordID, recordData, dirtyBit, partitionFacility, partitionUser))


	def superSetFilters ( self, filter ) :
		"""
		Input : filter
		Output : List of filters which are equal to or are superset of input filter
		"""
		superSet = []
		if self.syncDataStructure.has_key("*+*") :
			superSet.append("*+*")
		if filter[0] != "*" :
			if self.syncDataStructure.has_key(filter[0]+"+*") :
				superSet.append(filter[0]+"+*")
			if filter[1] != "*" :
				if self.syncDataStructure.has_key(filter[0]+"+"+filter[1]) :
					superSet.append(filter[0]+"+"+filter[1])
		return superSet
		

	def calcFSIC (self, filter ) :
		"""
		Given a filter(f), finds out maximum counter per instance for all 
		filters which are equal to or are superset of filter(f).
		"""
		# List of all superset filters
		superSetFilters = self.superSetFilters (filter)
		
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


	def findRecordInStore ( self, instanceID, counterLow, counterHigh, partitionFacility, partitionUser ) :
		records = []
		for key, value in self.store.items() :
			#Not included the condition for partition yet
			if value.partitionFacility == partitionFacility and value.lastSavedByInstance == instanceID and \
				(value.lastSavedByCounter >= counterLow and value.lastSavedByCounter <= counterHigh)  :
				if len(partitionUser) > 0 :
					if value.partitionUser == partitionUser :
						records.append(value)
				else :
					records.append(value) 
		return records


	def calcDiffFSIC ( self, fsic1, fsic2 , partFacility, partUser) :
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
					records = records + self.findRecordInStore(key, fsic2[key]+1, \
						fsic1[key]+1, partFacility, partUser)
					changes[key] = fsic1[key]
			else :
				records = records + self.findRecordInStore(key, 1, value+1, partFacility, partUser)
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


	def serialize (self, filter) :
		"""
		Input : Filter
		Serializes data from application(with dirty bit set) to store according to input filter
		"""
		for i in range(0, len(self.appData)) :
			tempAppData = self.appData[i]
			if tempAppData[2] and tempAppData[3] == filter[0] and tempAppData[4] == filter[1] :
				self.updateCounter()	
				# If store has a record with the same ID
				if self.store.has_key(tempAppData[0]) :
					temp = self.store[str(tempAppData[0])].lastSavedByHistory
					temp[str(self.instanceID)] = self.counter			
					record = StoreRecord(tempAppData[0], tempAppData[1], self.instanceID, \
						self.counter, temp, tempAppData[3], tempAppData[4])
				# Adding a new record with the given recordID
				else :
					record = StoreRecord(tempAppData[0], tempAppData[1], self.instanceID, \
						self.counter, {str(self.instanceID) : self.counter}, tempAppData[3], tempAppData[4])
				self.store[str(tempAppData[0])] = record
				# Clear dirty bit from data residing in the application
				self.appData[i] = self.appData[i][:2] + (0,) + tuple(self.appData[i][-2])
				# Making changes to Sync Data Structure 
				self.syncDataStructure["*+*"][str(self.instanceID)] = self.counter

	def integrate ( self ) :
		for key, value in self.incomingBuffer.items() :
			print "Receieved Data"
			for i in value[1][1] :
				self.integrateRecord(i)
                        	print i.recordID

                	# Update the sync data structure according to integrated data
                	self.updateSyncDS (value[1][0], value[0][0]+"+"+value[0][1])

			# After all the records from incoming buffer have been integrated to store
			del self.incomingBuffer[key]


	def integrateRecord (self, record) :
		"""
		Integrate record stored in Incoming Buffer to the store
		"""
		# If record exists in store check for merge-conflicts/fast-forward
		if self.store.has_key(record.recordID) :
			storeRecordHistory = self.store[record.recordID].lastSavedByHistory
			count = 0
			# Record's current version exists in storeRecord's history
			if storeRecordHistory.has_key(record.lastSavedByInstance) and \
				storeRecordHistory[record.lastSavedByInstance] > record.lastSavedByCounter :
				count = count + 1 
			# storeRecord's current version exists in record's history
			if record.lastSavedByHistory.has_key(self.store[record.recordID].lastSavedByInstance) and \
				record.lastSavedByHistory[self.store[record.recordID].lastSavedByInstance] > \
				self.store[record.recordID].lastSavedByCounter :
				count = count + 2
			#TO BE DONE LATER  		
		# Record does not exist in the store, add it
		else :
			self.store[str(record.recordID)] = record
	

	def fsicDiffAndSnapshot ( self, filter, receivedFSIC, pushPullID ) :
		# Create a copy of your FSIC
                localFSIC = self.calcFSIC(filter)
		# Calculates differences in local and remote FSIC
                extra = self.calcDiffFSIC(localFSIC, receivedFSIC, filter[0], filter[1])
		# Put all the data to be sent in outgoing buffer
		self.outgoingBuffer[pushPullID] = (filter, extra)
		

	def serviceRequests ( self ) :
		for i in range(0, len(self.requests)) :
			if self.requests[i][0] == "PULL" :
				self.fsicDiffAndSnapshot ( self.requests[i][3], self.requests[i][4], self.requests[i][1])

			elif self.requests[i][0] == "PUSH" :
				# Create a copy of your FSIC and sends it to client
                		localFSIC = self.calcFSIC(self.requests[i][3])
				self.requests[i][2].requests.append(("PUSH2", self.requests[i][1], localFSIC, self.requests[i][3]))
			
			elif self.requests[i][0] == "PUSH2" :
				self.fsicDiffAndSnapshot (self.requests[i][3], self.requests[i][2], self.requests[i][1])
				
			else :
				print "Request invalid!"
			# Delete the request after servicing
			del self.requests[i]

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
