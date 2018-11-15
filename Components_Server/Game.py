import base64
import socket
import struct
import time
import uuid

import sqlite3

import Utils.BlazeFuncs as BlazeFuncs
import Utils.Globals as Globals


def UpdateDataMysql(serverName, serverSlot, serverData, gameid):
	print('[SQLite] Creating server table...')

	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()
	
	seerverData_ = str(serverData)
	serverDataOk = base64.b64encode(seerverData_)
	
	#print("Name: " + str(serverName) + " Slot: " + str(serverSlot) + " Data: " + str(serverData))
	#cursor.execute("INSERT INTO `" + Globals.dbDatabase + "`.`serverslist` (`server_id`, `name`, `slot`, `data`) VALUES ('" + str(gameid) + "', '" + str(serverName) + "', '" + str(serverSlot) + "', '" + str(serverDataOk) + "');")
	cursor.execute("INSERT INTO `serverslist` (`server_id`, `name`, `slot`, `data`) VALUES ('" + str(gameid) + "', '" + str(serverName) + "', '" + str(serverSlot) + "', '" + str(serverDataOk) + "');")
	
	
	db.commit()
	cursor.close()
	db.close()

	print("[SQLite] Server table created in database, name: " + str(serverName))

	
def EditDataMysql(serverName, serverSlot, serverData, gameid):
	print('[SQLite] Editing server table...')

	db = sqlite3.connect(Globals.dbDatabase) 

	cursor = db.cursor()
	
	seerverData_ = str(serverData)
	serverDataOk = base64.b64encode(seerverData_)

	#cursor.execute("UPDATE `" + Globals.dbDatabase + "`.`serverslist` SET `name` = '" + str(serverName) + "', `slot` = '" + str(serverSlot) + "', `data` = '" + serverDataOk + "' WHERE `serverslist`.`server_id` = '" + str(gameid) + "';")
	cursor.execute("UPDATE `serverslist` SET `name` = '" + str(serverName) + "', `slot` = '" + str(serverSlot) + "', `data` = '" + serverDataOk + "' WHERE `serverslist`.`server_id` = '" + str(gameid) + "';")
	
	
	db.commit()
	cursor.close()
	db.close()

	print("[SQLite] Server table edited, name: " + str(serverName))
	
	
def CreateGame(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	
	self.GAMEOBJ.INTPORT = packet.getVarValue("PORT", 2)
	self.GAMEOBJ.EXTPORT = self.GAMEOBJ.INTPORT
	self.GAMEOBJ.GameID = Globals.curGID
	Globals.curGID += 1
	
	r_uuid = str(uuid.uuid4())
	self.GAMEOBJ.PGID = r_uuid
	self.GAMEOBJ.UUID = r_uuid

	self.GAMEOBJ.GameState = 1
	
	self.GAMEOBJ.GameSet = packet.getVar("GSET")
	ATTR_Name, ATTR_Cont = packet.getVar("ATTR")

	self.GAMEOBJ.AttrNames = ATTR_Name
	self.GAMEOBJ.AttrData = ATTR_Cont

	self.GAMEOBJ.MaxPlayers = packet.getVar("PCAP")[0]
	self.GAMEOBJ.MaxSpectat = packet.getVar("PCAP")[2]

	self.GAMEOBJ.GameRegis = packet.getVar("GMRG")
	self.GAMEOBJ.GameName = packet.getVar("GNAM")
	
	
	#mysql code
	UpdateDataMysql(self.GAMEOBJ.GameName, self.GAMEOBJ.MaxPlayers, self.GAMEOBJ.AttrData, self.GAMEOBJ.GameID)
	
	reply = BlazeFuncs.BlazePacket("0004","0001",packet.packetID,"1000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	reply = BlazeFuncs.BlazePacket("0004","0014","0000","2000")
	
	reply.writeSStruct("GAME")
	#reply.append("864b6e04000191a4e5bc02")
	
	reply.writeIntArray("ADMN")
	reply.writeBuildIntArray()
	
	
	reply.writeMap("ATTR")
	for i in range(len(self.GAMEOBJ.AttrNames)):
		reply.writeMapData(self.GAMEOBJ.AttrNames[i], self.GAMEOBJ.AttrData[i])
	reply.writeBuildMap()
	
	reply.writeIntArray("CAP ")
	reply.writeIntArray_Int(self.GAMEOBJ.MaxPlayers)
	reply.writeIntArray_Int(0)
	reply.writeIntArray_Int(self.GAMEOBJ.MaxSpectat)
	reply.writeIntArray_Int(0)
	reply.writeBuildIntArray()
	
	#reply.append("8e1c000400022000")
	
	reply.writeString("COID", "")
	
	reply.writeString("ESNM", "")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	reply.writeInt("GMRG", self.GAMEOBJ.GameRegis)
	reply.writeString("GNAM", self.GAMEOBJ.GameName)
	reply.writeInt("GPVH", 6667)
	reply.writeInt("GSET", self.GAMEOBJ.GameSet)
	reply.writeInt("GSID", 1337)
	reply.writeInt("GSTA", 1)
	reply.writeString("GTYP", "frostbite_multiplayer")
	reply.writeString("GURL", "")
	
	####
	reply.writeSArray("HNET")
	##Struct in array
	reply.append("030102")

	reply.writeSStruct("EXIP")
	reply.writeInt("IP  ", self.GAMEOBJ.EXTIP)
	reply.writeInt("PORT", self.GAMEOBJ.EXTPORT)
	reply.writeEUnion() #END EXIP
	
	reply.writeSStruct("INIP")
	reply.writeInt("IP  ", self.GAMEOBJ.INTIP)
	reply.writeInt("PORT", self.GAMEOBJ.INTPORT)
	reply.writeEUnion() #END INIP
	
	reply.writeEUnion() #END HNET
	##Struct array end
	
	reply.writeInt("HSES", 13666)
	reply.writeBool("IGNO", False)
	#reply.append("b63870008001")
	reply.writeInt("MCAP", 70)
	
	reply.writeSStruct("NQOS")
	reply.writeInt("DBPS", 0)
	reply.writeInt("NATT", 4)
	reply.writeInt("UBPS", 0)
	reply.writeEUnion() #END NQOS
	
	reply.writeBool("NRES", True)
	#NTOP 0 = CLIENT_SERVER_PEER_HOSTED
	#NTOP 1 = CLIENT_SERVER_DEDICATED
	reply.writeInt("NTOP", 1)
	
	reply.writeString("PGID", self.GAMEOBJ.PGID)
	reply.append("c27cf20238741aa5db00da730dab837a88f2088faef8662f8b43e09a4c34d7421e4d977e19958d55b9d025408f4082acd6f70d6690ffeb7fe437c7f905")

	reply.writeSStruct("PHST")
	reply.writeInt("HPID", self.GAMEOBJ.PersonaID)
	reply.writeInt("HSLT", 0)
	reply.writeEUnion() #END PHST
	
	#PRES 0 = NONE
	#PRES 1 = NORMAL
	#PRES 2 = PRIVATE
	reply.writeInt("PRES", 1)
	reply.writeString("PSAS", "ams")
	reply.writeInt("QCAP", 0)
	
	
	#cmdNames, cmdValues = packet.getVarValue("CRIT", 1)
	
	rcapCmd = packet.getVarValue("RCAP", 1)
	rcapSolider = packet.getVarValue("RCAP", 2)
	
	reply.writeSStruct("RNFO")
	reply.append("8f2a74050103") #CRIT
	
	
		
	if(rcapCmd <= 2):
		reply.append("02")
		
		reply.append("0a636f6d6d616e64657200") #COMMANDER
		reply.writeMap("CRIT")
		reply.writeMapData("commanderRank", "stats_rank >= 10")
		reply.writeBuildMap()
		reply.writeInt("RCAP", rcapCmd)
		reply.writeEUnion()
	else:
		reply.append("01")
		rcapSolider = rcapCmd
	
	reply.append("08736f6c6469657200") #SOLIDER
	reply.writeInt("RCAP", rcapSolider)
	reply.writeEUnion()
	reply.writeEUnion()
	
	reply.writeInt("SEED", 11181)
	
	reply.writeSStruct("THST")
	reply.writeInt("HPID", self.GAMEOBJ.PersonaID)
	reply.writeInt("HSLT", 0)
	reply.writeEUnion() #END THST
	
	reply.writeIntArray("TIDS")
	reply.writeIntArray_Int(65534)
	reply.writeBuildIntArray()
	
	reply.writeString("UUID", self.GAMEOBJ.UUID)
	reply.writeInt("VOIP", 0)
	reply.writeString("VSTR", "4900")
	reply.writeEUnion()
	
	reply.append("e2eba30200")
	reply.append("e339730200")
	
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
def FinalizeGameCreation(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	reply = BlazeFuncs.BlazePacket("0004","000f",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	reply = BlazeFuncs.BlazePacket("0004","0047","0000","2000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	reply.writeInt("PHID", self.GAMEOBJ.PersonaID)
	reply.writeInt("PHST", 0)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

	self.GAMEOBJ.IsUp = True

def setGameAttributes(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	ATTR_Name, ATTR_Cont = packet.getVar("ATTR")

	for i in range(len(self.GAMEOBJ.AttrNames)):
		for x in range(len(ATTR_Name)):
			if self.GAMEOBJ.AttrNames[i] == ATTR_Name[x]:
				self.GAMEOBJ.AttrData[i] = ATTR_Cont[x]

	reply = BlazeFuncs.BlazePacket("0004","0007",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	reply = BlazeFuncs.BlazePacket("0004","0050","0000","2000")
	reply.writeMap("ATTR")
	for i in range(len(ATTR_Name)):
		reply.writeMapData(ATTR_Name[i], ATTR_Cont[i])
	reply.writeBuildMap()
	reply.writeInt("GID ", self.GAMEOBJ.GameID)

	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
	#mysql code
	EditDataMysql(self.GAMEOBJ.GameName, self.GAMEOBJ.MaxPlayers, self.GAMEOBJ.AttrData, self.GAMEOBJ.GameID)

def setGameSettings(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	self.GAMEOBJ.GameSet = packet.getVar("GSET")

	reply = BlazeFuncs.BlazePacket("0004","0004",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	reply = BlazeFuncs.BlazePacket("0004","006E","0000","2000")
	reply.writeInt("ATTR", self.GAMEOBJ.GameSet)
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	

def UpdateMeshConnection(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	
	TCG =  packet.getVar("TCG ")
	
	#PID = TCG[1]-1
	PID = int(TCG[2])
	
	GID = self.GAMEOBJ.GameID
	STAT = packet.getVar("STAT")
	
	reply = BlazeFuncs.BlazePacket("0004","001d",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	if STAT == 2:

		for Client in Globals.Clients:
			if Client.PersonaID == PID:
				reply = BlazeFuncs.BlazePacket("7802","0001","0000","2000")
			
				reply.writeSStruct("DATA")
				reply.append("8649320602")
				
				reply.writeSStruct("VALU")
				reply.writeSStruct("EXIP")
				reply.writeInt("IP  ", Client.EXTIP)
				reply.writeInt("PORT", Client.EXTPORT)
				reply.writeEUnion() #END EXIP
				
				reply.writeSStruct("INIP")
				reply.writeInt("IP  ", Client.INTIP)
				reply.writeInt("PORT", Client.INTPORT)
				reply.writeEUnion() #END INIP
					
				reply.writeEUnion() #END VALU
				#reply.writeEUnion() #END DATA
				##Struct array end
				reply.append("8b0cc00104616d73008f4e400101008f6872070092d870050000028180382b8280388d06a379a70000c33b2d040006bfbff8ff01bfbff8ff01bfbff8ff01bfbff8ff01bfbff8ff01bfbff8ff01c6487403922c330000ba1d340004d62c33000000d61d3400808080808a58d6ccf40409010201" + reply.makeInt(Client.PersonaID) +"00")
				reply.writeInt("USID", Client.PersonaID)
				pack1, pack2 = reply.build()
				self.transport.getHandle().sendall(pack1.decode('Hex'))
				self.transport.getHandle().sendall(pack2.decode('Hex'))

				reply = BlazeFuncs.BlazePacket("0004","0074","0000","2000")
				reply.writeInt("GID ", GID)
				reply.writeInt("PID ", PID)
				reply.writeInt("STAT", 4)
				pack1, pack2 = reply.build()
				self.transport.getHandle().sendall(pack1.decode('Hex'))
				self.transport.getHandle().sendall(pack2.decode('Hex'))
			
				reply = BlazeFuncs.BlazePacket("0004","001e","0000","2000")
				reply.writeInt("GID ", GID)
				reply.writeInt("PID ", PID)
				pack1, pack2 = reply.build()
				self.transport.getHandle().sendall(pack1.decode('Hex'))
				self.transport.getHandle().sendall(pack2.decode('Hex'))
	else:

		leave = False
		for Client in Globals.Clients:
			if Client.PersonaID == int(PID):
				if(Client.Type == "Client"):
					self.GAMEOBJ.playerLeave(Client.PersonaID)
					leave = True
				elif(Client.Type == "Commander"):
					self.GAMEOBJ.playerLeaveCommander(Client.PersonaID)
					leave = True
				elif(Client.Type == "Spectator"):
					self.GAMEOBJ.playerLeaveSpectator(Client.PersonaID)
					leave = True
				
		if (leave):
			#0 Disconnected
			#1 Disconnect
			#2 Blaze Connection Lost
			#3 Migration Failed (P2P ?)
			reply = BlazeFuncs.BlazePacket("0004","0028","0000","2000")
			reply.writeInt("GID ", GID)
			reply.writeInt("PID ", PID)
			reply.writeInt("REAS", 1)
			pack1, pack2 = reply.build()
			self.transport.getHandle().sendall(pack1.decode('Hex'))
			self.transport.getHandle().sendall(pack2.decode('Hex'))
	
def AdvanceGameState(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	
	reply = BlazeFuncs.BlazePacket("0004","0003",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	State = packet.getVar("GSTA")
	
	self.GAMEOBJ.GameState = State
	
	reply = BlazeFuncs.BlazePacket("0004","0064","0000","2000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	reply.writeInt("GSTA", State)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

def replayGame(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	reply = BlazeFuncs.BlazePacket("0004","0013",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))

	reply = BlazeFuncs.BlazePacket("0004","0064","0000","2000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	reply.writeInt("GSTA", 130)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

def SetPlayerCapacity(self,data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	self.GAMEOBJ.MaxPlayers = packet.getVar("PCAP")[0]
	self.GAMEOBJ.MaxSpectat = packet.getVar("PCAP")[2]

	reply = BlazeFuncs.BlazePacket("0004","0005",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	reply = BlazeFuncs.BlazePacket("0004","006F","0000","2000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	
	rcapCmd = packet.getVarValue("RCAP", 1)
	rcapSolider = packet.getVarValue("RCAP", 2)
	
	
	if(rcapCmd <= 2):
		reply.append("02")
		
		reply.append("0a636f6d6d616e64657200") #COMMANDER
		reply.writeMap("CRIT")
		reply.writeMapData("commanderRank", "stats_rank >= 10")
		reply.writeBuildMap()
		reply.writeInt("RCAP", rcapCmd)
		reply.writeEUnion()
	else:
		reply.append("01")
		rcapSolider = rcapCmd
		
		
	reply.append("08736f6c6469657200") #SOLIDER
	reply.writeInt("RCAP", rcapSolider)
	reply.writeEUnion()
	reply.writeEUnion()
	
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
	#mysql code
	EditDataMysql(self.GAMEOBJ.GameName, self.GAMEOBJ.MaxPlayers, self.GAMEOBJ.AttrData, self.GAMEOBJ.GameID)
	
def UpdateGameName(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	self.GAMEOBJ.GameName = packet.getVar("GNAM")

	packet = BlazeFuncs.BlazeDecoder(data_e)
	reply = BlazeFuncs.BlazePacket("0004","0027",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	#mysql code
	EditDataMysql(self.GAMEOBJ.GameName, self.GAMEOBJ.MaxPlayers, self.GAMEOBJ.AttrData, self.GAMEOBJ.GameID)
	
def SetGameModRegister(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	packet = BlazeFuncs.BlazeDecoder(data_e)
	gmrg = packet.getVar("GMRG")
	self.GAMEOBJ.GameRegis = gmrg

	reply = BlazeFuncs.BlazePacket("0004","0029",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	reply = BlazeFuncs.BlazePacket("0004","007B","0000","2000")
	reply.writeInt("GMID", self.GAMEOBJ.GameID)
	reply.writeInt("GMRG", self.GAMEOBJ.GameRegis)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
def swapPlayersTeam(self, data_e):
	packet = BlazeFuncs.BlazeDecoder(data_e)
	reply = BlazeFuncs.BlazePacket("0004","0070",packet.packetID,"1000")
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	pid = packet.getVar("PID ")
	role = packet.getVar("ROLE")
	slot = packet.getVar("SLOT")
	tidx = packet.getVar("TIDX")
	
	
	reply = BlazeFuncs.BlazePacket("0004","0075","0000","2000")
	reply.writeInt("GID ", self.GAMEOBJ.GameID)
	reply.writeInt("PID ", pid)
	reply.writeString("ROLE", role)
	reply.writeInt("SLOT", 0)
	reply.writeInt("TIDX", 0)
	
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
	for Client in Globals.Clients:
		if Client.PersonaID == pid:
			Client.Type = "Commander"
			if(self.GAMEOBJ.playerLeave(pid)):
				if(self.GAMEOBJ.playerJoinCommander(pid) != False):
					Client.NetworkInt.getHandle().sendall(pack1.decode('Hex'))
					Client.NetworkInt.getHandle().sendall(pack2.decode('Hex'))

def ReciveComponent(self,func,data_e):
	func = func.upper()
	if func == "0001":
		print("[GMGR] CreateGame")
		CreateGame(self,data_e)
	elif func == "0002":
		print("[GMGR] DestroyGame")
	elif func == "0003":
		print("[GMGR] AdvanceGameState")
		AdvanceGameState(self,data_e)
	elif func == "0004":
		print("[GMGR] SetGameSettings")
		setGameSettings(self,data_e)
	elif func == "0005":
		print("[GMGR] SetPlayerCapacity")
		SetPlayerCapacity(self,data_e)
	elif func == "0006":
		print("[GMGR] SetPresenceMode")
	elif func == "0007":
		print("[GMGR] SetGameAttributes")
		setGameAttributes(self,data_e)
	elif func == "0008":
		print("[GMGR] SetPlayerAttributes")
	elif func == "0009":
		print("[GMGR] JoinGame")
		JoinGame(self,data_e)
	elif func == "000B":
		print("[GMGR] RemovePlayer")
	elif func == "000D":
		print("[GMGR] StartMatchMaking")
	elif func == "000E":
		print("[GMGR] CancelMatchMaking")
	elif func == "000F":
		print("[GMGR] FinalizeGameCreation")
		FinalizeGameCreation(self,data_e)
	elif func == "0011":
		print("[GMGR] ListGames")
	elif func == "0012":
		print("[GMGR] SetPlayerCustomData")
	elif func == "0013":
		print("[GMGR] ReplayGame")
		replayGame(self,data_e)
	elif func == "0014":
		print("[GMGR] returnDedicatedServerToPool")
	elif func == "0015":
		print("[GMGR] JoinGameByGroup")
	elif func == "0016":
		print("[GMGR] leaveGameByGroup")
	elif func == "0017":
		print("[GMGR] migrateGame")
	elif func == "0018":
		print("[GMGR] updateGameHostMigrationStatus")
	elif func == "0019":
		print("[GMGR] resetDedicatedServer")
	elif func == "001A":
		print("[GMGR] UpdateGameSession")
	elif func == "001B":
		print("[GMGR] BanPlayer")
	elif func == "001D":
		print("[GMGR] UpdateMeshConnection")
		UpdateMeshConnection(self,data_e)
	elif func == "001F":
		print("[GMGR] RemovePlayerFromBannedList")
	elif func == "0020":
		print("[GMGR] ClearBannedList")
	elif func == "0021":
		print("[GMGR] getBannedList")
	elif func == "0026":
		print("[GMGR] addQueuedPlayerToGame")
	elif func == "0027":
		print("[GMGR] updateGameName")
		UpdateGameName(self, data_e)
	elif func == "0028":
		print("[GMGR] ejectHost")
	elif func == "0029":
		print("[GMGR] setGameModRegister")
		SetGameModRegister(self, data_e)
	elif func == "0064":
		print("[GMGR] getGameListSnapshot")
	elif func == "0065":
		print("[GMGR] getGameListSubscription")
	elif func == "0066":
		print("[GMGR] DestoryGameList")
	elif func == "0067":
		print("[GMGR] getFullGameData")
	elif func == "0068":
		print("[GMGR] GetMatchmakingConfig")
	elif func == "0069":
		print("[GMGR] GetGameDataFromID")
	elif func == "006A":
		print("[GMGR] AddAdminPlayer")
	elif func == "006B":
		print("[GMGR] RemoveAdminPlayer")
	elif func == "006C":
		print("[GMGR] SetPlayerTeam")
	elif func == "006D":
		print("[GMGR] ChangeGameTeamID")
	elif func == "006E":
		print("[GMGR] MigrateAdminPlayer")
	elif func == "006F":
		print("[GMGR] GetUserSetGameListSubscription")
	elif func == "0070":
		print("[GMGR] SwapPlayersTeam")
		swapPlayersTeam(self, data_e)
	elif func == "0096":
		print("[GMGR] RegisterDynamicDedicatedServerCreator")
	elif func == "0097":
		print("[GMGR] UN-RegisterDynamicDedicatedServerCreator")
	else:
		print("[GMGR] ERROR! UNKNOWN FUNC "+func)
