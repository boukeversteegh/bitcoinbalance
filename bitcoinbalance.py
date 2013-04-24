#from lib import cherrypy
import cherrypy
import sys
import json
import os.path
import datetime, time
import os
import pystache
import urllib2

import mtgox.api
import mtgox.ticker
import timecache

def formatTimeStamp(ts):
	date = datetime.datetime.fromtimestamp(int(ts))
	return date.strftime("%b %d, %Y %H:%M:%S")

class MyRenderer(pystache.Renderer):
	def str_coerce(self, val):
		if val is None:
			return ""
		return str(val)

def template(path, args={}):
	renderer = MyRenderer(file_extension='partial', search_dirs=['www/partials'])
	#mapdict(xstr, args)
	return renderer.render_path(os.path.join('www', 'tpl', path), args)

class BitcoinBalance:
	def __init__(self):
		api = mtgox.api.Api()
		self.mtgoxticker = mtgox.ticker.Ticker(api,60*5)
		self.tcache = timecache.TimeCache(60*5)
		
	def getBTC(self, address):
		try:
			url="http://blockchain.info/q/addressbalance/%s" % address
			response = urllib2.urlopen(url)
			data = response.read()
			return float(data)/100000000.0
		except urllib2.HTTPError:
			raise Exception("Invalid Address: %s" % address)
	
	def default(self, addresses=""):
		tdata = {}
		addresses = addresses.replace('+', ' ')
		addresses = addresses.strip()
		if len(addresses) > 0:
			addresses = addresses.split(' ')
			tdata['addresses'] = addresses
		else:
			tdata['addresses'] = []
		return template('index.html', tdata)
	default.exposed=True

	def balance(self, addresses=None):
		tdata = {}
		try:
			mtgoxusd = self.mtgoxticker.getRate('USD')
			mtgoxeur = self.mtgoxticker.getRate('EUR')

			rates = {
				"mtgox-USD": '%.2f' % mtgoxusd,
				"mtgox-EUR": '%.2f' % mtgoxeur
			}
			tdata['rates'] = rates

			if addresses is None:
				return template('index.html')

			addresses = addresses.strip()
			addresses = addresses.replace('+', ' ')
			addresses = addresses.split(' ')

			tdata['addresses'] = addresses

			addresses = list(set(addresses))

			btc = 0

			now = int(time.time())
			min_btc_timestamp = now
			for address in addresses:
				if len(address) == 0:
					continue

				btc+= self.tcache.get(self.getBTC,address)
				_, btc_timestamp = self.tcache.getTSCache(self.getBTC,address)
				min_btc_timestamp = min(min_btc_timestamp, btc_timestamp)

			tdata['addresses'] = addresses
			
			balance = {
				"BTC": '%.8f' % btc,
				"mtgox-USD": '%f' % (btc * mtgoxusd),
				"mtgox-EUR": '%f' % (btc * mtgoxeur)
			}
			tdata['balance'] = balance
			tdata['btc_timestamp'] = formatTimeStamp(min_btc_timestamp)
			tdata['btc_age'] = str(datetime.timedelta(seconds=now-int(min_btc_timestamp)))
			return template('balance.html', tdata);
		except Exception as e:
			tdata['error'] = str(e)
			return template('index.html', tdata);
		
	balance.exposed=True

if __name__ == '__main__':
	
	conf = {
		'/': {
			'tools.staticdir.on': True,
			'tools.staticdir.dir': os.path.join(os.getcwd(), 'www/wwwpublic')
		},
		'/favicon.ico': {
			'tools.staticfile.on': True,
			'tools.staticfile.filename': "/path/to/favicon.ico"
		}
    }


	root	= BitcoinBalance()
	cherrypy.config.update({
		'server.socket_host': '0.0.0.0', 
		'server.socket_port': 8800
	})

	cherrypy.quickstart(root, '/', conf)
