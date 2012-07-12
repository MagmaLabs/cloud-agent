from twisted.application import service
from twisted.application.internet import TimerService

from cloudagent.util.importTools import importAllSubclassing

from cloudagent.Metric import Metric

import time
try:
	import simplejson as json
except ImportError:
	import json

class MetricService(TimerService):
	def __init__( self, metricProvider ):
		TimerService.__init__( self, metricProvider.getInterval( ), self.processMetrics )
		self.metricProvider = metricProvider
	
	def processMetrics( self ):
		metrics = self.metricProvider.getMetrics( )
		if metrics is not None:
			if 'time' not in metrics:
				metrics['time'] = time.time()
			print json.dumps( metrics )

application = service.Application( 'cloudagent' )

# find the metrics
def _getMetricProviders( ):
	for metricClass in importAllSubclassing( 'cloudagent.metrics', Metric ):
		metricInst = metricClass( )
		if metricInst.supported( ):
			yield metricInst
		else:
			print 'Ignoring', metricClass.__name__, '(not supported on this system)'

# add the metric providers to the application as services
for metricProvider in _getMetricProviders( ):
	metricService = MetricService( metricProvider )
	metricService.setServiceParent( application )
