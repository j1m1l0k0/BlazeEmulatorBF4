import socket
import struct
import threading

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol

import Utils.BlazeFuncs as BlazeFuncs
import Utils.Globals as Globals


class GOSRedirector(Protocol):
	def dataReceived(self, data):
		data_e = data.encode('Hex')
		packet = BlazeFuncs.BlazeDecoder(data.encode('Hex'))
		
		## REDIRECTORCOMPONENT
		if packet.packetComponent == '0005' and packet.packetCommand == '0001':
			clnt = packet.getVar("CLNT")
			
			port = 10040
			if clnt == "warsaw server":
				port = 10071
			
			#ip = ''.join([ bin(int(x))[2:].rjust(8,'0') for x in Globals.serverIP.split('.')])
			ip = struct.unpack("!I", socket.inet_aton(socket.gethostbyname(Globals.serverIP)))[0]
			
			if clnt == "warsaw client":
				Globals.serverIP = "localhost"
				ip = 2130706433
			
			reply = BlazeFuncs.BlazePacket("0005","0001",packet.packetID,"1000")
			reply.writeSUnion("ADDR")
			reply.writeSStruct("VALU")
			reply.writeString("HOST", Globals.serverIP)
			reply.writeInt("IP  ", ip)
			
			reply.writeInt("PORT", port)
			reply.writeEUnion()
			reply.writeInt("SECU", 0)
			reply.writeInt("XDNS", 0)
			self.transport.write(reply.build().decode('Hex'))
