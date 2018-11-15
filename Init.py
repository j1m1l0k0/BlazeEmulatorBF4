#! python2.7
import sqlite3
import sys
import platform

from twisted.internet import reactor, ssl
from twisted.internet.protocol import Factory, Protocol
from twisted.web import resource, server

import BlazeMain_Client
import BlazeMain_Server
import GosRedirector
import Https
import Utils.Globals as Globals
from Utils import garbage

sys.dont_write_bytecode = True

def Start():

	Globals.serverIP = "127.0.0.1"
	
	Globals.dbDatabase = "database/bf4.db"
	
	CheckMySqlConn()
		
	SSLInfo = ssl.DefaultOpenSSLContextFactory('crt/privkey.pem', 'crt/cacert.pem')
	
	factory = Factory()
	factory.protocol = GosRedirector.GOSRedirector
	reactor.listenSSL(42127, factory, SSLInfo)
	print("[SSL REACTOR] GOSREDIRECTOR STARTED [42127]")
	
	factory = Factory()
	factory.protocol = BlazeMain_Client.BLAZEHUB
	reactor.listenTCP(10041, factory)
	print("[TCP REACTOR] BLAZE CLIENT [10041]")
	
	factory = Factory()
	factory.protocol = BlazeMain_Server.BLAZEHUB
	reactor.listenTCP(10071, factory)
	print("[TCP REACTOR] BLAZE SERVER [10071]")
	
	sites = server.Site(Https.Simple())
	reactor.listenSSL(443, sites, SSLInfo)
	print("[WEB REACTOR] Https [443]")
	
	reactor.run()
	
	
def CheckMySqlConn():
	
	osversion = (platform.system() + ' ' + platform.release())
	print('''
	-/- Blaze Emulator BF4 - Version SQLite3 by j1m1l0k0 - %s
	''' % osversion)
	
	print("[SQLite] Checking server connection...")
	
	try:
		db = sqlite3.connect(Globals.dbDatabase)
		cursor = db.cursor()        
		cursor.execute("SELECT SQLITE_VERSION()")
		results = cursor.fetchone()

		print("[SQLite Version: %s] Server connection ok!" % results)
		
	except sqlite3.Error, e:
		print "[SQLite] Server connection failed! Error: %d in connection: %s" % (e.args[0], e.args[1])
		sys.exit()
		

if __name__ == '__main__':
	Start()
