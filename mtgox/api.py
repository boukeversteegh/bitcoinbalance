import urllib
import urllib2
import json

class ApiException(Exception): pass

class Api:
	host = 'http://mtgox.com'
	useragent = 'BitcoinBalance'

	def _build_query(self, request={}):
		headers = {
			"User-Agent": self.useragent
		}
		postdata = urllib.urlencode(request)
		return (postdata, headers)

	def query(self, path, args={}):
		postdata, headers = self._build_query(args)
		url = self.host+path

		if postdata == '':
			request		= urllib2.Request(url, headers=headers)
			response	= urllib2.urlopen(request, timeout=5)
		else:
			request		= urllib2.Request(url, headers=headers, data=postdata)
			response	= urllib2.urlopen(request, postdata, timeout=5)


		data		= json.load(response)
		
		if data['result'] == 'success':
			returndata	= data['return']
			return returndata
		else:
			raise ApiException(data['error'])


from hashlib import sha512
from hmac import HMAC
import base64
import time

class PrivateApi(Api):
	host = 'https://mtgox.com'

	def __init__(self, key, secret):
		self.key	= key
		self.secret	= base64.b64decode(secret)

	def _get_nonce(self):
		return int(time.time()*100000)
	
	def _sign_data(self, secret, data):
		return base64.b64encode(str(HMAC(secret, data, sha512).digest()))

	def _build_query(self, request={}):
		request["nonce"] = self._get_nonce()
		postdata, headers = Api._build_query(self, request)
		
		headers["Rest-Key"]		= self.key
		headers["Rest-Sign"]	= self._sign_data(self.secret, postdata)
		return (postdata, headers)

if __name__ == "__main__":
	from timecache import TimeCache
	mtgox = Api()
	timecache = TimeCache(10)

	while True:
		print timecache.getWait(mtgox.query, '/api/1/BTCUSD/ticker')
