# morango
Simulation of MorangoDB

Short description of each file and folder contents.

1. simulateNode.py : Class definition for device instance. Every device contains Application layer, Store, Incoming buffer and Outgoing buffer. It also contains various drivers for initiating and completing operations like serialzation, integration, inflation etc.  
2. appRecord.py : Class definition for application records saved in the Application layer of device instance. The records contain record ID, record data, partition details and dirty bit. The file also contains different functions which can be applied on application records for example clearing and setting the dirty bit, resolving merge conflicts etc. 
3. storeRecord.py : Class definition for store records saved in the Store layer of device instance. The records contain record ID, data, partition details, record version(Last Saved Bys) and Record Max Counters(LastSavedByHistory). It also contains various operations on storeRecords such as comparing the record versions for 2 given store records.
4. syncSession.py : Class definition for sync session object which is stored at both the devices taking part in the sync session.
5. readFile.py : Code to read the files in results folder. It also calculates the average over multiple simulations
6. testMorango.py : Contains testcases. For example : Checking if eventual consistency has been achieved if a few nodes go offline, checking the correctness of various operations(merge-conflict resolution on 2 parallel nodes with same data). 
7. Folder results : Contains result files for different experiments ran.
8. Folder oldTestFiles : Ignore, Outdated tests.

Run the following command on terminal to run testcases :
python testMorango.py
