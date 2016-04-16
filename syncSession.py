class SyncSession:

	# Sync Session ID
	syncSessID = None
	# Client morango instance ID 
	clientInstance = None
	# Server morango instance ID 
	serverInstance = None
	# Incremented on a PUSH/PULL request
	requestCounter = None

	def __init__( self, syncSessID, clientInstance, serverInstance):
		"""
		Constructor
		"""
		self.syncSessID = syncSessID
		self.clientInstance = clientInstance
		self.serverInstance = serverInstance
		self.requestCounter = 0


	def incrementCounter ( self ) :
		"""
		Initiation of a new PUSH/PULL request
		"""
		self.requestCounter = self.requestCounter + 1


	def pushInitiation ( self, filter ) :
		"""
        	Push request initialized by client with filter
        	"""
        	# Step 1 : Client sends Push request along with filter to Server
        	# Step 2 : Server caluclates its FSIC and sends it to Client
        	serverFSIC = self.serverInstance.calcFSIC(filter)
        	# Step 3 : Client creates its own FSIC locally 
        	clientFSIC = self.clientInstance.calcFSIC(filter)
        	# Step 4 : Client calculates the differences and sees what needs to be pushed
        	clientExtra = self.clientInstance.calcDiffFSIC(clientFSIC, serverFSIC, filter[0], filter[1])
        	# Step 5 : Client sends the data to server according to ClientExtra
        	# Step 6 : Server makes changes to its sync Data Structure, after receiving the records 
        	self.serverInstance.updateSyncDS( clientExtra[0], filter[0]+"+"+filter[1])
		# Directly integrating data received by client into server's store
		for i in clientExtra[1] :
			self.serverInstance.integrateRecord(i, "*+*")
		print "Data sent by client"
		for i in clientExtra[1]:
			print i.recordID
        	#printServerClientConfig(client, server)


	def pullInitiation (self, filter) :
        	"""
        	Pull request initialized by client with filter
        	"""
		# Step 1 : Client calcualtes the PULL ID
		pullID = str(self.syncSessID) + "_" + str(self.requestCounter)
		# Increment the counter for next session
		self.incrementCounter()
        	# Step 2 : Client calculates its FSIC locally
        	clientFSIC = self.clientInstance.calcFSIC(filter)
		# Step 3 : Client sends pullID, filter and its FSIC to server
		self.serverInstance.requests.append(("PULL", pullID, self.clientInstance, filter, clientFSIC))


	def printServerClientConfig(self) :
        	# Print client as well as server configurations 
        	print "Server"
        	self.serverInstance.printNode()
        	print "Client"
        	self.clientInstance.printNode()

	def dataExchange (self, sender, receiver, bufferSize ) :
		for key,value in sender.outgoingBuffer.items() :
			receiver.incomingBuffer[key] = value
			# Delete the entry from Incoming buffer
			del sender.outgoingBuffer[key] 		

	def printSyncSession ( self ) :
		"""
		Pretty-printing all the variable values residing in SyncSession Object
		"""
		print "Sync Session ID :" + str(self.syncSessID)
		print "Client Instance :" + str(self.clientInstance)
		print "Server Instance  :" + str(self.serverInstance)
			
