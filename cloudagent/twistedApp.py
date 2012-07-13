from twisted.application import service
from twisted.application.internet import TimerService

from cloudagent.util.importTools import importAllSubclassing

from cloudagent.Metric import Metric
from cloudagent.MetricService import MetricService
from cloudagent.PushService import PushService

import time
import os
import sys
try:
	import simplejson as json
except ImportError:
	import json

try:
	import agent_settings
except ImportError:
	print 'You need to create an "agent_settings.py" file.'
	sys.exit( 1 )

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

# add a service to check for files spooled and ready to push
pushService = PushService( )
pushService.setServiceParent( application )