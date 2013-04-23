import time
from cache import Cache, CacheException

class TimeCache(Cache):
	def __init__(self, maxage):
		Cache.__init__(self)
		self.maxage = maxage

	def getTSCache(self, *args):
		#print 'TimeCache.getCache(%s)' % repr(args)
		value, timestamp = super(TimeCache, self).getCache(*args)
		
		if time.time() > timestamp + self.maxage:
			raise CacheException("Expired")

		return value, timestamp

	def getCache(self, *args):
		return self.getTSCache(*args)[0]

	def setCache(self, value, *args):
		#print 'TimeCache.setCache(%s)' % repr(value)
		timestamp = time.time()
		super(TimeCache, self).setCache((value, timestamp), *args)

	def getWait(self, *args):
		try:
			value, timestamp = self.getTSCache(*args)

			expiretime	= (timestamp + self.maxage)
			waittime	= expiretime-time.time()

			if waittime > 0:
				time.sleep(waittime)
		except CacheException as e:
			#print '!! getWait: %s' % e
			pass

		return self.getFresh(*args)


if __name__ == "__main__":
	cache = TimeCache(2)
	import time, datetime
	print '--'
	print 'now:'.ljust(30), cache.get(time.time)
	#.sleep(3)
	print '1 second later, cached:'.ljust(30), cache.get(time.time)
	#print '1 second later, force wait:'.ljust(30), cache.getWait(time.time)
	#print 'datetime, force wait:'.ljust(30), cache.getWait(datetime.datetime.today)
	print 'datetime, force wait:'.ljust(30), cache.getWait(datetime.datetime.today)
