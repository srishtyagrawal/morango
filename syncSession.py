class SyncSession:

	# Sync Session ID
	syncSessID = None
	# Client morango instance ID 
	clientInstance = None
	# Server morango instance ID 
	serverInstance = None


	def __init__( self, syncSessID, clientInstance, serverInstance):
		"""
		Constructor
		"""
		self.syncSessID = syncSessID
		self.clientInstance = clientInstance
		self.serverInstance = serverInstance


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
        	clientExtra = self.clientInstance.calcDiffFSIC(clientFSIC, serverFSIC, filter)
        	# Step 5 : Client sends the data to server according to ClientExtra
        	# Step 6 : Server makes changes to its sync Data Structure, after receiving the records 
        	self.serverInstance.updateSyncDS( clientExtra[0], filter)
		# Directly integrating data received by client into server's store
		for i in clientExtra[1] :
			self.serverInstance.integrateRecord(i, "*")
		'''
		print "Data sent by client"
		for i in clientExtra[1]:
			i.printStoreRecord()
		'''
        	#printServerClientConfig(client, server)


	def pullInitiation (self, filter) :
        	"""
        	Pull request initialized by client with filter
        	"""
        	# Step 1 : Client calculates its FSIC locally
        	clientFSIC = self.clientInstance.calcFSIC(filter)
        	# Step 2 : Client sends filter and its FSIC to server
        	# Step 3 : Server creates its FSIC locally
        	serverFSIC = self.serverInstance.calcFSIC(filter)
        	# Step 4 : Server calculates differences in FSIC
        	serverExtra = self.serverInstance.calcDiffFSIC(serverFSIC, clientFSIC, filter)
        	# Step 5 : Server sends data to client which abides by serverExtra
        	# Step 6 : Client updates its syncDataStructure
        	self.clientInstance.updateSyncDS (serverExtra[0], filter)
		# Directly integrating data received by server into client's store
		for i in serverExtra[1] :
			self.clientInstance.integrateRecord(i, "*")	
		'''
		print "Data sent by server"
		for i in serverExtra[1] :
			i.printStoreRecord()
		'''
        	#printServerClientConfig(client, server)

	def printServerClientConfig(self) :
        	# Print client as well as server configurations 
        	print "Server"
        	self.serverInstance.printNode()
        	print "Client"
        	self.clientInstance.printNode()

	#def dataExchange (self, filter ) :
		# To be filled according to on-demand batch sizes!

	def printSyncSession ( self ) :
		"""
		Pretty-printing all the variable values residing in SyncSession Object
		"""
		print "Sync Session ID :" + str(self.syncSessID)
		print "Client Instance :" + str(self.clientInstance)
		print "Server Instance  :" + str(self.serverInstance)
			
