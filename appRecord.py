class AppRecord:

	# Record Unique ID
	recordID = None
	# Serialized Record Data
	recordData = None
	# dirty bit
	dirtyBit = None
	# Partition information for this record
	partitionFacility = None
	partitionUser = None

	def __init__( self, recordID, recordData, partitionFacility, partitionUser):
		"""
		Constructor
		"""
		if len(recordID) == 0 :
                        raise ValueError('Length of recordID should be greater than 0')
		self.recordID = recordID
		self.recordData = recordData
		self.dirtyBit = 1
		self.partitionFacility = partitionFacility
		self.partitionUser = partitionUser


	def clearDirtyBit(self) :
		"""
		Clears the dirty bit on serialization
		"""
		self.dirtyBit = 0


	def setDirtyBit(self) :
		"""
		Sets the dirty bit on adding new data
		"""
		self.dirtyBit = 1

		
	def updateRecordData(self, data) :
		"""
		Changes replaces old record data with newly supplied data
		"""
		self.recordData = data


	def printAppRecord ( self ) :
		"""
		Pretty-printing all the variable values residing in AppRecord Object
		"""
		print "App Record ID :" + str(self.recordID)
		print "Record Data :" + str(self.recordData)
		print "Dirty Bit:" + str(self.dirtyBit) 	
		print "Partitions Facility:" + str(self.partitionFacility) + " User:"+ str(self.partitionUser)	
