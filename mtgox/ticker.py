import timecache

class Ticker:
	def __init__(self, api, interval=10):
		self.api = api
		self.cache	= timecache.TimeCache(interval)

	def getUrl(self, url):
		return self.cache.get(self.api.query, url)
	
	def getRate(self, currency):
		data = self.getUrl('/api/1/BTC{currency}/ticker'.format(currency=currency))
		return float(data['last']['value'])
