from twisted.application import service
from twisted.application.internet import TimerService

class MetricService(TimerService):
	def __init__( self, metricProvider ):
		super(MetricService, self).__init__( metricProvider.getInterval( ), self.processMetrics )
		self.metricProvider = metricProvider
	
	def processMetrics( self ):
		metrics = self.metricProvider.getMetrics( )
		if metrics is not None:
			if 'time' not in metrics:
				metrics['time'] = time.time()
			print json.dumps( metrics )

application = service.Application( 'cloudagent' )

# find the metrics
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

# add the metric providers to the application as services
for metricProvider in _getMetricProviders( ):
	metricService = MetricService( metricProvider )
	metricService.setServiceParent( application )
