import threading

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol

import Utils.BlazeFuncs as BlazeFuncs
import Utils.DataClass as DataClass
import Utils.Globals as Globals
from Components_Client import Accounts
from Components_Client import Authentication as Auth
from Components_Client import Friends, Game, Inventory, Packs, Stats, Unknown
from Components_Client import UserSessions as UserSe
from Components_Client import Util


class BLAZEHUB(Protocol):
	GAMEOBJ = None
	DATABUFF = ""
	
	def connectionMade(self):
		#print "Connect from", self.transport.getPeer().port
		try:
			self.transport.setTcpKeepAlive(1)
		except AttributeError: pass
		
	def connectionLost(self, reason):
		#print "Disconnect from", self.transport.getPeer()
		port = self.transport.getPeer().port
		for auth in Globals.authClients:
			if auth.Port == port:
				Globals.authClients.remove(auth)
		
		if self.GAMEOBJ != None:
			self.GAMEOBJ.IsUp = False
			
	def dataReceived(self, data):
		data_e = data.encode('hex')
		allData = False

		if len(self.DATABUFF) != 0 and self.DATABUFF != data_e:
			self.DATABUFF = self.DATABUFF+data_e
			data_e = self.DATABUFF

		dataLenghth = (int(data_e[:4], 16)*2)+24
		if len(data_e) >= dataLenghth:
			if len(self.DATABUFF) != 0:
				self.DATABUFF = ""
			allData = True
			data_1 = data_e[:dataLenghth]
			data_2 = data_e[dataLenghth:]

			if len(data_2) > 0:
				self.dataReceived(data_2.decode('Hex'))
		elif len(data_e) < dataLenghth and self.DATABUFF == "":
			self.DATABUFF = data_e
      
		if allData == True:
			packet = BlazeFuncs.BlazeDecoder(data_1)
			if packet.packetComponent == '0001':
				Auth.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0004':
				Game.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0007':
				Stats.ReciveComponent(self,packet.packetCommand,data_e)  
			elif packet.packetComponent == '0009':
				Util.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0019':
				Friends.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0023':
				Accounts.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '7802':
				UserSe.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0801':
				Unknown.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0802':
				Packs.ReciveComponent(self,packet.packetCommand,data_e)
			elif packet.packetComponent == '0803':
				Inventory.ReciveComponent(self,packet.packetCommand,data_e)
			else:
				print("[BLAZE CLIENT] ERROR!! Unhandled Comonent("+packet.packetComponent+") and Function("+packet.packetCommand+")")
