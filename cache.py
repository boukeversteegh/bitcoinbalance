import collections

class CacheException(Exception): pass

class Cache(object):
	def __init__(self):
		self.clear()

	def clear(self):
		tree = lambda: collections.defaultdict(tree)
		self.cache = tree()

	def _hash(self, step):
		if isinstance(step, dict):
			return repr(step)
		return step

	def getCache(self, *args):
		#print 'Cache.getCache(%s)' % repr(args)
		args = [self._hash(step) for step in args]

		cachelocation = self.cache
		for step in args[:-1]:
			cachelocation = cachelocation[step]

		if args[-1] in cachelocation:
			return cachelocation[args[-1]]
		else:
			raise CacheException("Not in cache")

	def setCache(self, value, *args):
		#print 'Cache.setCache(%s, %s)' % (repr(value), repr(args))
		args = [self._hash(step) for step in args]
		cachelocation = self.cache
		for step in args[:-1]:
			cachelocation = cachelocation[step]
		cachelocation[args[-1]] = value

	def getFresh(self, *args):
		if hasattr(args[0], '__call__'):
			fargs = list(args)
			func = fargs.pop(0)
			value = func(*fargs)
			self.setCache(value, *args)
			return value

	def get(self, *args):
		try:
			return self.getCache(*args)
		except CacheException:
			return self.getFresh(*args)

if __name__ == "__main__":
	c = Cache()

	class Foobar:
		def slow(self, arg):
			import time
			time.sleep(1)
			return arg*10
	
	foobar = Foobar()
	print c.get(foobar.slow, 2)
	print c.get(foobar.slow, 3)
	print c.get(foobar.slow, 2)


	def pdict(d):
		import time
		time.sleep(1)
		return d['key']

	print c.get(pdict, {"key":"foobar"})
	print c.get(pdict, {"key":"foobar"})
	print c.get(pdict, {"key":"foobar"})