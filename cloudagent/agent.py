try:
	import simplejson as json
except ImportError:
	import json

import time

modules = [
	'Memory',
	'Network'
]

def _getMetricProviders( ):
	for module in modules:
		className = module + 'Metric'
		metricModule = __import__( 'metrics.' + className, globals(), locals(), [className] )
		metricClass = getattr( metricModule, className )
		metricInst = metricClass( )
		yield metricInst

metricProvider = list( _getMetricProviders( ) )

for metricInst in metricProvider:
	metrics = metricInst.getMetrics()
	if metrics is not None:
		data = metrics
		if 'time' not in data:
			data['time'] = time.time()
		print json.dumps( data )