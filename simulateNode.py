from storeRecord import StoreRecord
from syncSession import SyncSession
from copy import deepcopy
import hashlib

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
	# Dictionary of session objects
	sessions = None

	ALL = ""
	GENERIC = None

	def __init__( self, instanceID):
		"""
		Constructor
		"""
		if len(instanceID) == 0 :
			raise ValueError('Length of instanceID should be greater than 0')
		self.instanceID = instanceID
		# Initiate a node with counter position 0
		self.counter = 0
		# Add an entry for full replication containing own instance ID and counter position
		self.syncDataStructure = {Node.ALL + "+" + Node.ALL:{str(self.instanceID):self.counter}} 
		self.store = {}
		self.incomingBuffer = {}
		self.appData = []
		self.outgoingBuffer = {}
		self.sessions = {}


	def updateCounter ( self ) :
		"""
		Increment counter by 1 when data is saved/modified
		"""
		self.counter = self.counter + 1


	def addAppData ( self, recordID, recordData, partitionFacility, partitionUser) :
		"""
		Adding records to the application
		"""
		# Third argument is the dirty bit which will always be set for new data
		self.appData.append((recordID, recordData, 1, partitionFacility, partitionUser))


	def superSetFilters ( self, filter ) :
		"""
		Input  : filter
		Output : List of filters which are equal to or are superset of input filter
		"""
		superSet = []
		# Add the full replication entry from Sync Data Structure		
		if self.syncDataStructure.has_key(Node.ALL + "+" + Node.ALL) :
			superSet.append(Node.ALL + "+" + Node.ALL)
		else :
			raise ValueError("No full replication entry in Sync Datastructure of node " + self.instanceID)

		if filter[0] != Node.ALL :
			if self.syncDataStructure.has_key(filter[0]+"+" + Node.ALL) :
				superSet.append(filter[0]+"+"+ Node.ALL)
			# User partition is specifically mentioned
			if filter[1] != Node.ALL :
				if self.syncDataStructure.has_key(filter[0]+"+"+filter[1]) :
					superSet.append(filter[0]+"+"+filter[1])
		return superSet
		

	def calcFSIC (self, filter ) :
		"""
		Given a filter(f), finds out maximum counter per instance for all 
		filters which are superset of filter(f).
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
		Makes changes to syncDataStructure after data has been integrated to the Store	
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


	def isSubset ( self, filter1, filter2 ) :
		"""
		Return a boolean value if filter1 is a subset of filter2
		"""
		if filter2[0] == Node.ALL and filter2[1] == Node.ALL :
			return True 
		elif filter2[0] == Node.ALL and filter2[1] != Node.ALL :
			raise ValueError("Facility ALL but User not ALL")
		elif filter2[0] != Node.ALL :
			if filter1[0] == filter2[0] :
				if filter2[1] == Node.ALL :
					return True
				elif filter2[1] != Node.ALL and filter2[1] == filter1[1] :
					return True
		return False


	def findRecordInStore ( self, instanceID, counterLow, counterHigh, partitionFacility, partitionUser ) :
		records = []
		for key, value in self.store.items() :
			recordCounter = value.lastSavedByCounter
			recordInstance = value.lastSavedByInstance

			if recordCounter >= counterLow and recordCounter <= counterHigh and recordInstance == instanceID :
				# Full replication condition, get all the records
				if self.isSubset ((value.partitionFacility, value.partitionUser), (partitionFacility, partitionUser)) :
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
			if tempAppData[2] and self.isSubset((tempAppData[3], tempAppData[4]),filter) :
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
				self.syncDataStructure[Node.ALL + "+" + Node.ALL][str(self.instanceID)] = self.counter


	def deserialize(self) :
		"""
		Convert records in store to application data
		"""
		for key,value in self.store.items() :
			# flag used to avoid duplication as appData is list and not dictionary
			flag = 0
			for i in range (len(self.appData)):
				# record exists in the application
				if self.appData[i][0] == key :
					flag = 1
					# If dirty bit is set then new changes were made 
					if self.appData[i][2] == 1 :
						raise ValueError('Merge Conflict while derializing data')
					# If dirty bit is not set, then overwrite the data 
					else :
						self.appData[i] = (key, value.recordData, 0, value.partitionFacility,\
							value.partitionUser)	
			# If the recordID does not exist in the application
			if flag == 0 :
				self.appData.append((key, value.recordData, 0, value.partitionFacility, value.partitionUser))
			

	def integrate ( self ) :
		for key, value in self.incomingBuffer.items() :
			for i in value[1][1] :
				self.integrateRecord(i)

                	# Update the sync data structure according to integrated data
                	self.updateSyncDS (value[1][0], value[0][0]+"+"+value[0][1])

			# After all the records from incoming buffer have been integrated to store
			del self.incomingBuffer[key]


	def compareVectors (self, v1, v2) :
		"""
		Return 0 if v1 is smaller than v2
		       1 if v2 is smaller than v1 
		       2 if there is a merge conflict i.e there is no ordering between v1 and v2
		       3 if v1 is same as v2
		"""
		# Checking if two vectors are equal
		temp = set()
		if len(v1) == len(v2) :
			for key,value in v1.items() :
				if v2.has_key(key) and v2[key] == v1[key] :
					temp.add(3)
				else :
					temp.add(9)
		if len(temp) == 1 and (3 in temp) :
			return temp
		temp = set()

		# Checking is v1 is smaller than v2
		for key, value in v1.items() :
			if v2.has_key(key) and v2[key] >= v1[key] :
				temp.add(0)
			else :
				temp.add(2)
		if len(temp) == 1 and (0 in temp) :
			return 0

		# Checking if v2 is smaller than v1
		temp = set()
		for key,value in v2.items() :
			if v1.has_key(key) and v1[key] >= v2[key] :
				temp.add(1)
			else :
				temp.add(3)
		if len(temp) == 1 and (1 in temp) :
			return 1 	
		else :
			return 2


	def integrateRecord (self, record) :
		"""
		Integrate record stored in Incoming Buffer to the store
		"""
		# If record exists in store check for merge-conflicts/fast-forward
		if self.store.has_key(record.recordID) :
			storeRecordHistory = self.store[record.recordID].lastSavedByHistory
			if self.compareVectors(storeRecordHistory, record.lastSavedByHistory) == 2 :
				raise ValueError('Merge Conflict while integration')
			elif self.compareVectors(storeRecordHistory, record.lastSavedByHistory) == 1  :
				self.store[str(record.recordID)] = record
			elif self.compareVectors(storeRecordHistory, record.lastSavedByHistory) == 0 \
				or self.compareVectors(storeRecordHistory, record.lastSavedByHistory) == 3:
				return		
			else :
				raise ValueError ("Invalid return from compare vector method!")
		# Record does not exist in the store, add it
		else :
			self.store[str(record.recordID)] = record
	

	def fsicDiffAndSnapshot ( self, filter, receivedFSIC ) :
		"""
		Input : remote FSIC, filter
		Output : Transfers data to be sent in the outgoing buffer
		"""
		# Create a copy of your FSIC
                localFSIC = self.calcFSIC(filter)
		# Calculates differences in local and remote FSIC
                extra = self.calcDiffFSIC(localFSIC, receivedFSIC, filter[0], filter[1])
		# Put all the data to be sent in outgoing buffer
		return (filter, extra)
		

	def queue (self, pushPullID, filter, snapshot) :
		"""
		Put data obtained after snapshotting in outgoing buffer
		"""
		self.outgoingBuffer[pushPullID] = (filter, snapshot) 


	def createSyncSession ( self, serverInstance, serverInstanceID) :
		"""
		Create a sync session and send ID and client's instance to server
		"""
		ID = hashlib.md5(self.instanceID).hexdigest() + hashlib.md5(serverInstanceID).hexdigest()
		self.sessions[ID] = SyncSession(ID, None, serverInstance )
		serverInstance.initialHandshake(ID, self)
		return ID


	def initialHandshake( self, ID, clientInstance) :
                """
       		Store sync session details you have received from Client
                """
                self.sessions[ID] = SyncSession(ID, clientInstance , None )


	def serviceRequests ( self ) :
		"""
		Services the ongoing requests in sessions object
		"""
		for k in self.sessions :
			request = self.sessions[k].ongoingRequest 
			client = self.sessions[k].clientInstance

			if request and request[0] == "PULL" :
				filter, snapshot = self.fsicDiffAndSnapshot ( request[2], request[3])
				self.queue(request[1], filter, snapshot)
				self.send(client, k, ("DATA", request[1], self.outgoingBuffer[(request[1])]))
				del self.outgoingBuffer[request[1]]
				self.sessions[k].ongoingRequest = None

			elif request and request[0] == "PUSH" :
				# Create a copy of your FSIC and sends it to client
                		localFSIC = self.calcFSIC(request[2])
				# PUSH2 request : ("PUSH2", pushID, filter, localFSIC)
				self.send(client, k, ("PUSH2", request[1], request[2], localFSIC))
				self.sessions[k].ongoingRequest = None
		
			elif request and request[0] == "PUSH2" :
				filter, snapshot = self.fsicDiffAndSnapshot (request[2], request[3])
				self.queue(request[1], filter, snapshot)
				self.send(self.sessions[k].serverInstance, k, ("DATA", request[1], self.outgoingBuffer[request[1]]))
				self.sessions[k].ongoingRequest = None
			
			elif request :
				raise ValueError('Invalid Request!')


	def pullInitiation (self, syncSessID, filter) :
		"""
                Pull request initialized by client with filter
                """
		syncSessObj = self.sessions[syncSessID]
                # Step 1 : Client calcualtes the PULL ID
                pullID = str(syncSessObj.syncSessID) + "_" + str(syncSessObj.requestCounter)
                # Increment the counter for next session
                syncSessObj.incrementCounter()
                # Step 2 : Client calculates its FSIC locally
                localFSIC = self.calcFSIC(filter)
                # Step 3 : Client sends pullID, filter and its FSIC to server
		self.send (syncSessObj.serverInstance, syncSessID, ("PULL", pullID, filter, localFSIC))


        def pushInitiation ( self, syncSessID , filter ) :
                """
                Push request initialized by client with filter
                """
		syncSessObj = self.sessions[syncSessID]
                # Step 1 : Client calcualtes the PUSH ID
                pushID = str(syncSessObj.syncSessID) + "_" + str(syncSessObj.requestCounter)
                # Increment the counter for next session
                syncSessObj.incrementCounter()
                # Step 3 : Client sends pushID and filter to server
		self.send (syncSessObj.serverInstance, syncSessID, ("PUSH", pushID, filter))


	def send (self, receiver, sessionID, data) :
		"""
		The only API through which a device communicates with another device
		"""
		receiver.receive(self, sessionID, data)


	def receive (self, sender, sessionID, data) :
		"""
		Action to be taken once data arrives on a device
		"""
		if data[0] == "PULL" or data[0] == "PUSH" or data[0] == "PUSH2":
			self.sessions[sessionID].ongoingRequest = data
			self.serviceRequests()

		elif data[0] == "DATA" :
			self.incomingBuffer[data[1]] = data[2]
			self.integrate()	
		

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
