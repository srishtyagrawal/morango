class StoreRecord:

	# Record Unique ID
	recordID = None
	# Serialized Record Data
	recordData = None
	# Last morango Instance's ID which saved/modified the record 
	lastSavedByInstance = None
	# Last morango Instance's counter position which saved/modified the record
	lastSavedByCounter = None
	# List of unique instance ID, counter(highest) pairs which have modified this record in past
	lastSavedByHistory = None


	def __init__( self, recordID, recordData, lastSavedByInstance, lastSavedByCounter, lastSavedByHistory):
		"""
		Constructor
		"""
		self.recordID = recordID
		self.recordData = recordData
		self.lastSavedByInstance = lastSavedByInstance
		self.lastSavedByCounter = lastSavedByCounter
		self.lastSavedByHistory = lastSavedByHistory


	def updateRecord (self, serializedData, instanceID, counter) :
		if self.updateLastSavedByHistory(instanceID, count):
			self.updateLastSavedByInstanceCounter(instanceID, count)
			self.updateRecordData(serializedData)
		else :
			print "Outdated record Data"
		
	def updateRecordData(self, serializedData) :
		self.recordData = serializedData


	def updateLastSavedByInstanceCounter ( self, instanceID , count ) :
		"""
        	Lastest modification made to the record by instance with ID instanceID at counter position count
        	"""
		self.lastSavedByInstance = instanceID
		self.lastSavedByCounter = count
		# make changes to lastSavedByHistory
		self.updatelastSavedByHistory( instanceID, count)


	def updateLastSavedByHistory (self, instanceID, count) :
		if self.lastSavedByHistory :
			# Searching for the instance is lastSavedByHistory list
			for i in range(0, len(self.lastSavedByHistory)) :
				if self.lastSavedByHistory[i][0] == instanceID
					# instance ID found and its counter is outdated 
					if self.lastSavedByHistory[i][1] < count :
						del self.lastSavedByHistory[i]
						# Most recent entry goes to the end of the list
						self.lastSavedByHistory.append((instanceID, count))
						return True
					# instance ID found and its counter is up-to-date
					else :
						return False
			self.lastSavedByHistory.append((instanceID, count))
			return True
		# Adding first entry to lastSavedByHistory
		else :
			self.lastSavedByHistory = [(instanceID,count)]
			return True


	def printStoreRecord ( self ) :
		"""
		Pretty-printing all the variable values residing in StoreRecord Object
		"""
		print "Store Record ID :" + str(self.recordID)
		print "Record Data :" + str(self.recordData)
		print "Last Saved by Instance & respective Counter position :" + str(self.lastSavedByInstance) + " " + str(self.lastSavedByCounter)
		print "Last Saved by History : " + str(self.lastSavedByHistory)
			
