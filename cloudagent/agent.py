try:
	import simplejson as json
except ImportError:
	import json

import time

data = {}
data['time'] = time.time()

modules = [
	'Memory',
	'Network'
]

for module in modules:
	className = module + 'Metric'
	metricModule = __import__( 'metrics.' + className, globals(), locals(), [className] )
	metricClass = getattr( metricModule, className )
	metricInst = metricClass( )
	metrics = metricInst.getMetrics()
	if metrics is not None:
		data.update( metrics['data'] )

print json.dumps( data )