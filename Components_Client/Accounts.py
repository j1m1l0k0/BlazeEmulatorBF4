import os
import socket
import struct

import Utils.BlazeFuncs as BlazeFuncs
import Utils.DataClass as DataClass
import Utils.Globals as Globals


def getUserSessionFromAuth(self, data_e):
	if self.GAMEOBJ == None:
		self.GAMEOBJ = DataClass.BF3Client()
		self.GAMEOBJ.NetworkInt = self.transport

	packedIP = socket.inet_aton(self.transport.getPeer().host)
	self.GAMEOBJ.EXTIP = struct.unpack("!L", packedIP)[0]
	self.GAMEOBJ.IsUp = True

	packet = BlazeFuncs.BlazeDecoder(data_e)
	
	name = packet.getVar("AUTH")
	
	port = self.transport.getPeer().port
	
	print "Client connecting by port = " + str(port)
	for auth in Globals.authClients:
		if auth.Port == port:
			name = auth.Name
			print name+" Authed By Port"
	
	cwd = os.getcwd()
	path = cwd+"\\Users\\"+name+"\\"
	'''
	if name == "":
		print "No account..."
		#self.transport.loseConnection()
		return

	if not os.path.exists(path):
		print "No account folder exists..."
		#self.transport.loseConnection()
		return
	'''
	id = 0
	for c in name:
		id += ord(c)
		
	self.GAMEOBJ.PersonaID = id
	self.GAMEOBJ.UserID = id
	self.GAMEOBJ.Name = name
	
	Globals.Clients.append(self.GAMEOBJ)
	
	reply = BlazeFuncs.BlazePacket("0023","000a",packet.packetID,"1000")
	reply.writeBool("ANON", False)
	reply.writeBool("NTOS", False)
	#SESS STRUCT START
	reply.writeSStruct("SESS")
	reply.writeInt("BUID", self.GAMEOBJ.PersonaID)
	reply.writeBool("FRSC", False)
	reply.writeBool("FRST", False)
	reply.writeString("KEY ", "SessionKey_1337")
	reply.writeInt("LLOG", 1403663841)
	reply.writeString("MAIL", self.GAMEOBJ.EMail)
		
	#PDTL STRUCT START
	reply.writeSStruct("PDTL")
	reply.writeString("DSNM", self.GAMEOBJ.Name)
	reply.writeInt("PID ",self.GAMEOBJ.PersonaID)
	reply.writeInt("PLAT", 4)
	reply.writeEUnion() # END PDTL
	reply.writeInt("UID ",self.GAMEOBJ.PersonaID)
	reply.writeEUnion() #END SESS
	
	reply.writeBool("SPAM", True)
	reply.writeBool("UNDR", False)
	self.transport.getHandle().sendall(reply.build().decode('Hex'))
	
	reply = BlazeFuncs.BlazePacket("7802","0008","0000","2000")
	reply.writeInt("ALOC", 1403663841)
	reply.writeInt("BUID", 321422442)
	reply.append("8E7A640982E003029DE68780808080C03F")
	reply.writeString("DSNM",self.GAMEOBJ.Name)
	reply.writeBool("FRSC", False)
	reply.writeBool("FRST", False)
	reply.writeString("KEY ","SessionKey_1337")
	reply.writeInt("LAST", 1403663841)
	reply.writeInt("LLOG", 1403663841)
	reply.writeString("MAIL", self.GAMEOBJ.EMail)
	reply.writeInt("PID ", self.GAMEOBJ.PersonaID)
	reply.writeInt("PLAT", 4)
	reply.writeInt("UID ", self.GAMEOBJ.PersonaID)
	reply.writeInt("USTP", 0)
	reply.writeInt("XREF", 0)
	pack1, pack2 = reply.build()
	
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

	reply = BlazeFuncs.BlazePacket("7802","0002","0000","2000")
	reply.writeSStruct("DATA")
	reply.append("864932067f") #ADDR
	reply.writeString("BPS ", "")
	reply.writeString("CTY ", "")
	reply.append("8f68720700") #CVAR
	reply.writeInt("HWFG", 0)
	
	reply.writeSStruct("QDAT")
	reply.writeInt("DBPS", 0)
	reply.writeInt("NATT", 0)
	reply.writeInt("UBPS", 0)
	reply.writeEUnion() #END QDAT
	
	#reply.writeInt("UATT", 0)
	reply.append("D61D3400808080D081A409")
	reply.append("D6CCF404090182E003029DE68780808080C03F")
	reply.writeEUnion() #END DATA
	
	reply.writeSStruct("USER")
	reply.writeInt("AID ", self.GAMEOBJ.UserID)
	reply.writeInt("ALOC", 1701729619)
	reply.writeInt("ID  ", self.GAMEOBJ.PersonaID)
	reply.writeString("NAME", self.GAMEOBJ.Name)
	reply.writeInt("ORIG", self.GAMEOBJ.PersonaID)
	reply.writeInt("PIDI", self.GAMEOBJ.PersonaID)
	reply.writeEUnion() #END USER
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))
	
	reply = BlazeFuncs.BlazePacket("7802","0005","0000","2000")
	reply.writeInt("FLGS", 3)
	reply.writeInt("ID  ", self.GAMEOBJ.PersonaID)
	pack1, pack2 = reply.build()
	self.transport.getHandle().sendall(pack1.decode('Hex'))
	self.transport.getHandle().sendall(pack2.decode('Hex'))

def ReciveComponent(self,func,data_e):
	func = func.upper()
	if func == '000A':
		print("[ACCTS] getUserSessionFromAuth")
		getUserSessionFromAuth(self,data_e)
	else:
		print("[ACCTS] ERROR! UNKNOWN FUNC "+func)
