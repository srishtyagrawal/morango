class SyncSession:

	# Sync Session ID
	syncSessID = None
	# Client morango instance ID 
	clientInstance = None
	# Server morango instance ID 
	serverInstance = None
	# Incremented on a PUSH/PULL request
	requestCounter = None
	# Ongoing request 
	ongoingRequest = None

	def __init__( self, syncSessID, clientInstance, serverInstance):
		"""
		Constructor
		"""
		self.syncSessID = syncSessID
		self.clientInstance = clientInstance
		self.serverInstance = serverInstance
		self.requestCounter = 0
		self.ongoingRequest = None


	def incrementCounter ( self ) :
		"""
		Initiation of a new PUSH/PULL request
		"""
		self.requestCounter = self.requestCounter + 1


	def printServerClientConfig(self) :
        	# Print client as well as server configurations 
        	print "Server"
        	self.serverInstance.printNode()
        	print "Client"
        	self.clientInstance.printNode()


	def printSyncSession ( self ) :
		"""
		Pretty-printing all the variable values residing in SyncSession Object
		"""
		print "Sync Session ID :" + str(self.syncSessID)
		print "Client Instance :" + str(self.clientInstance)
		print "Server Instance  :" + str(self.serverInstance)
			
