from appRecord import AppRecord 

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
	# Partition information for this record
	partitionFacility = None
	partitionUser = None

	def __init__( self, recordID, recordData, lastSavedByInstance, lastSavedByCounter, lastSavedByHistory, partitionFacility, partitionUser):
		"""
		Constructor
		"""
		if len(recordID) == 0 :
                        raise ValueError('Length of recordID should be greater than 0')
		self.recordID = recordID
		self.recordData = recordData
		self.lastSavedByInstance = lastSavedByInstance
		self.lastSavedByCounter = lastSavedByCounter
		self.lastSavedByHistory = lastSavedByHistory
		self.partitionFacility = partitionFacility
		self.partitionUser = partitionUser


	def updateRecord (self, serializedData, instanceID, counter) :
		"""
		Input : record data, instanceID 
		"""
		if self.updateLastSavedByHistory(instanceID, count):
			self.updateLastSavedByInstanceCounter(instanceID, count)
			self.updateRecordData(serializedData)
		else :
			print "Outdated record Data"

		
	def updateRecordData(self, data) :
		"""
		Changes replaces old record data with newly supplied data
		"""
		self.recordData = data


	def updateLastSavedByInstanceCounter ( self, instanceID , counter ) :
		"""
        	Lastest modification made to the record by instance with instanceID at counter position
        	"""
		self.lastSavedByInstance = instanceID
		self.lastSavedByCounter = counter


	def updateLastSavedByHistory (self, instanceID, count) :
		"""
		Return False if record's lastSavedByHistory is up to date
		Return True if modifictaion in lastSavedByHIstory is needed
		"""
		if self.lastSavedByHistory :
			# Searching for the instance in lastSavedByHistory
			if self.lastSavedByHistory.has_key(str(instanceID)) :
				# instance ID found and its counter is outdated 
				if self.lastSavedByHistory[str(instanceID)] < count :
					self.lastSavedByHistory[str(instanceID)] = count
					return True
				# instance ID found and its counter is up-to-date
				else :
					return False
			else :
				self.lastSavedByHistory[str(instanceID)] = count
				return True
		# Adding first entry to lastSavedByHistory
		else :
			self.lastSavedByHistory = {str(instanceID):count}
			return True


        def inflateRecord ( self) :
                """
                Convert a storeRecord to an application record
                Not adding the record to appData yet
                """
                # Dirty bit is turned off by default
                record = AppRecord(self.recordID, self.recordData, self.partitionFacility, \
                        self.partitionUser)
                record.clearDirtyBit()
                return record


	def printStoreRecord ( self ) :
		"""
		Pretty-printing all the variable values residing in StoreRecord Object
		"""
		print "Store Record ID :" + str(self.recordID)
		print "Record Data :" + str(self.recordData)
		print "Last Saved by Instance & respective Counter position :" + str(self.lastSavedByInstance) + " " + str(self.lastSavedByCounter)
		print "Last Saved by History : " + str(self.lastSavedByHistory)
		print "Partitions Facility:" + str(self.partitionFacility) + " User:"+ str(self.partitionUser)	
