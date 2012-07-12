import simplejson as json

import time

data = {}
data['time'] = time.time()

modules = [
	'Memory',
	'Network'
]

for module in modules:
	className = module + 'Metric'
	metric = __import__( 'metrics.' + className, globals(), locals(), [className] )
	metrics = metric.getMetrics()
	if metrics is not None:
		data.update( metrics['data'] )

print json.dumps( data )