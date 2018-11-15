import Utils.BlazeFuncs as BlazeFuncs 
import Utils.Globals as Globals
import sqlite3

def ReciveComponent(self,func,data_e):
	func = func.upper()
	
	#print data_e
	#print "================"
	if func == '0064':
		print("[GMRPT] submitTrustedMidGameReport")
		packet = BlazeFuncs.BlazeDecoder(data_e)
		
		pids, content = packet.getStatsVar("PLYR")
	
		for i in range(len(pids)):
			pid = int(pids[i])
			
			name = None
			for Client in Globals.Clients:
				if Client.PersonaID == pid:
					name = Client.Name

			#stats = open('Users/'+name+'/userstats.txt', 'r')
			pStats = []
			lines = loadMySql(name, "userstats").splitlines() #check me
		   	#lines = stats.readlines()
		   	#stats.close()

		   	lines = [word.strip() for word in lines]

		   	for line in lines:
		   		pStats.append(line.split("="))

			for x in range(len(content[i])):
				for y in range(len(pStats)):
					if (content[i][x][0][:-2] == pStats[y][0]) or (content[i][x][0] == pStats[y][0]):
						stat = float(content[i][x][1])
						stat = stat+float(pStats[y][1])
						pStats[y][1] = str(stat)

			#f = open("Users/"+name+"/userstats.txt", 'w')
			statsToWrite = ""
			for y in range(len(pStats)):
				#f.write(pStats[y][0]+"="+pStats[y][1]+"\n")
				statsToWrite = statsToWrite+pStats[y][0]+"="+pStats[y][1]+"\n"
				
			writeMySql(name, statsToWrite, "userstats")
			statsToWrite = ""
			#f.close()
		
		reply = BlazeFuncs.BlazePacket("001C","0064",packet.packetID,"1000")
		self.transport.getHandle().sendall(reply.build().decode('Hex'))
		
		reply = BlazeFuncs.BlazePacket("001C","0072","0000","2000")

		#Funkay Data
		reply.append("921d21070194b6e4a50c")
		
		reply.writeSStruct("DATA")
		reply.writeIntArray("PLYR")
		for i in range(len(pids)):
			reply.writeIntArray_Int(int(pids[i]))
		reply.writeBuildIntArray()
		
		reply.writeEUnion()
		reply.writeEUnion()
		
		reply.writeInt("EROR", 0)
		reply.writeInt("FNL ", 0)
		reply.writeInt("GHID", 1000000)
		reply.writeInt("GRID", 1000000)

		pack1, pack2 = reply.build()
		
		self.transport.getHandle().sendall(pack1.decode('Hex'))
		self.transport.getHandle().sendall(pack2.decode('Hex'))
	elif func == '0065':
		print("[GMRPT] submitTrustedEndGameReport")
		packet = BlazeFuncs.BlazeDecoder(data_e)

		reply = BlazeFuncs.BlazePacket("001C","0065",packet.packetID,"1000")
		self.transport.getHandle().sendall(reply.build().decode('Hex'))
		
		pids, content = packet.getStatsVar("PLYR")
		
		reply = BlazeFuncs.BlazePacket("001C","0072","0000","2000")
		
		#Funkay Data
		reply.append("921d21070194b6e4a50c")
		
		reply.writeSStruct("DATA")
		reply.writeIntArray("PLYR")
		for i in range(len(pids)):
			reply.writeIntArray_Int(int(pids[i]))
		reply.writeBuildIntArray()
		
		reply.writeEUnion()
		reply.writeEUnion()
		
		reply.writeInt("EROR", 0)
		reply.writeInt("FNL ", 1)
		reply.writeInt("GHID", 1000000)
		reply.writeInt("GRID", 1000000)
		
		pack1, pack2 = reply.build()
		self.transport.getHandle().sendall(pack1.decode('Hex'))
		self.transport.getHandle().sendall(pack2.decode('Hex'))
		
	else:
		print("[GMRPT] ERROR! UNKNOWN FUNC "+func)
		
		
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