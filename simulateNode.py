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
	# Pending requests queue
	requests = None
	# Dictionary of session objects
	sessions = None

	ALL = ""
	GENERIC = None

	def __init__( self, instanceID):
		"""
		Constructor
		"""
		self.instanceID = instanceID
		self.counter = 0
		self.syncDataStructure = {Node.ALL + "+" + Node.ALL:{str(self.instanceID):self.counter}} 
		self.store = {}
		self.incomingBuffer = {}
		self.appData = []
		self.outgoingBuffer = {}
		self.requests = []
		self.sessions = {}


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
		if self.syncDataStructure.has_key(Node.ALL + "+" + Node.ALL) :
			superSet.append(Node.ALL + "+" + Node.ALL)
		if filter[0] != Node.ALL :
			if self.syncDataStructure.has_key(filter[0]+"+" + Node.ALL) :
				superSet.append(filter[0]+"+"+ Node.ALL)
			if filter[1] != Node.ALL :
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
		"""
		Input : remote FSIC, filter, pushPullID
		Output : Transfers data to be sent in the outgoing buffer
		"""
		# Create a copy of your FSIC
                localFSIC = self.calcFSIC(filter)
		# Calculates differences in local and remote FSIC
                extra = self.calcDiffFSIC(localFSIC, receivedFSIC, filter[0], filter[1])
		# Put all the data to be sent in outgoing buffer
		self.outgoingBuffer[pushPullID] = (filter, extra)
		

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
				self.fsicDiffAndSnapshot ( request[2], request[3], request[1])
				self.dataSend(client, request[1], 10)
				self.sessions[k].ongoingRequest = None

			elif request and request[0] == "PUSH" :
				# Create a copy of your FSIC and sends it to client
                		localFSIC = self.calcFSIC(request[2])
				# PUSH2 request : ("PUSH2", pushID, filter, localFSIC)
				client.sessions[k].ongoingRequest = ("PUSH2", request[1], request[2], localFSIC)
				client.serviceRequests()
				self.sessions[k].ongoingRequest = None
		
			elif request and request[0] == "PUSH2" :
				self.fsicDiffAndSnapshot (request[2], request[3], request[1])
				self.dataSend(self.sessions[k].serverInstance, request[1], 10)
				self.sessions[k].ongoingRequest = None
			
			elif request :
				print "Request invalid!"


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
		#syncSessObj.ongoingRequest = ("PULL started", pullID, filter)
                syncSessObj.serverInstance.sessions[syncSessID].ongoingRequest = ("PULL", pullID, filter, localFSIC)
		syncSessObj.serverInstance.serviceRequests()


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
                syncSessObj.serverInstance.sessions[syncSessID].ongoingRequest = ("PUSH", pushID, filter)
		syncSessObj.serverInstance.serviceRequests()


        def dataSend (self, receiver, pushPullID, bufferSize ) :
		"""
		Transfers data pertaining to a push/pull request in outgoing buffer 
		to receiver's incoming buffer
		"""
                receiver.incomingBuffer[pushPullID] = self.outgoingBuffer[pushPullID]
                # Delete the entry from Incoming buffer
                del self.outgoingBuffer[pushPullID]
		receiver.integrate()


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
