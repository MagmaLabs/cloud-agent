from twisted.application.internet import TimerService

from cloudagent.SpoolJournal import SpoolJournal

import time
import os
import bson

SPOOL_DIR = 'spool'
METRICS_SPOOL_DIR = os.path.join( SPOOL_DIR, 'metrics' )

if not os.path.exists( METRICS_SPOOL_DIR ):
	os.makedirs( METRICS_SPOOL_DIR )
metricJournals = SpoolJournal( METRICS_SPOOL_DIR )

class MetricService(TimerService):
	def __init__( self, metricProvider ):
		TimerService.__init__( self, metricProvider.getInterval( ), self.processMetrics )
		self.metricProvider = metricProvider
	
	def processMetrics( self ):
		metrics = self.metricProvider.getMetrics( )
		if metrics is not None:
			if 'time' not in metrics:
				metrics['time'] = time.time()
				metrics['unique_id'] = str( bson.objectid.ObjectId( ) )
			metricJournals.writeData( metrics )