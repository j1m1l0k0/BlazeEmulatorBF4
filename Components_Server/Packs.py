import json

import sqlite3

import Utils.BlazeFuncs as BlazeFuncs
import Utils.Globals as Globals


def grantPacks(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	packList = packet.getVar("PKLS")
	userID = packet.getVar("UID ")
	
	reply = BlazeFuncs.BlazePacket("0802","0002",packet.packetID,"1000")
	reply.writeArray("PIDL")
	for i in range(len(packList)):
		reply.writeArray_TInt("ERR ", 0)
		reply.writeArray_TString("PKEY", packList[i])
		reply.writeArray_ValEnd()
	reply.writeBuildArray("Struct")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	name = None
	for Client in Globals.Clients:
		if Client.UserID == userID:
			name = Client.Name
			
	if name == None:
		return
	
	#itemsFile = open('Users/'+name+'/items.txt', 'r')
   	#Items = itemsFile.readlines()
	items = loadMySql(name, "items")
	itemToWrite = items
	for x in range(len(packList)):
		if not (packList[x] in items):
			#itemFile.write(packList[x]+"\n")
			itemToWrite = itemToWrite+packList[x]+"\n"
			
			battlepackItem = [packList[x], []]

			#battlepackFile = open('Users/'+name+'/battlepacks.txt', 'r')
			#packStr = battlepackFile.readline()
			#battlepackFile.close()
			packStr = loadMySql(name, "battlepacks")
			
			writeDta = []
			if len(packStr) <= 2:
				writeDta = [battlepackItem]
			else:
				battlepacks = json.loads(packStr)
				battlepacks.append(battlepackItem)
				writeDta = battlepacks
			
			#battlepackFile = open('Users/'+name+'/battlepacks.txt', 'w')
			#battlepackFile.write(json.dumps(writeDta))
			#battlepackFile.close()
			writeMySql(name, json.dumps(writeDta), "battlepacks")
			
	writeMySql(name, itemToWrite, "items")
	itemToWrite = ""
	#itemFile.close()


def ReciveComponent(self,func,data_e):
	func = func.upper()
	if func == '0002':
		print("[PACKS] grant Packs")
		grantPacks(self,data_e)
	else:
		print("[INV] ERROR! UNKNOWN FUNC "+func)

def loadMySql(user, field):
	#Query example: SELECT usersettings FROM `users` WHERE username = 'StoCazzo' 
	
	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()

	sql = "SELECT "+str(field)+" FROM `users` WHERE username = '"+str(user)+"'"
	
	try:
	   cursor.execute(sql)
	   results = cursor.fetchall()
	   for row in results:
		  returnData = row[0]
		  return returnData
	except:
	   print "[SQLite] Can't load field: " + str(field) + " user: " + str(user) + " from SQLite!"

	db.close()
	
def writeMySql(user, data, field):
	#Query Example: UPDATE `users` SET `usersettings` = 'helloguys' WHERE `users`.`username` = 'StoCazzo'
	
	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()

	sql = "UPDATE `users` SET `"+str(field)+"` = '"+str(data)+"' WHERE `users`.`username` = '"+str(user)+"'"
		
	try:
	   cursor.execute(sql)
	   db.commit()
	except:
	   print "[SQLite] Can't write field: " + str(field) + " and data: " + str(data) + " to SQLite!"
	   db.rollback()

	db.close()
