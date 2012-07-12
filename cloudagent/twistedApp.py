from twisted.application import service
from twisted.application.internet import TimerService

from cloudagent.util.importTools import importAllSubclassing

from cloudagent.Metric import Metric

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

print 'push:', agent_settings.PUSH_DETAILS

class SpoolJournal(object):
	MAX_RECORDS_PER_FILE = 1000
	
	def __init__( self, path ):
		self._filePath = path
		
		self._currentPath = os.path.join( path, 'current' )
		self._completePath = os.path.join( path, 'complete' )
		
		if not os.path.exists( self._completePath ):
			os.makedirs( self._completePath )
		
		self._file = None
		self._doRotate( )
	
	def writeData( self, data ):
		self._maybeRotate( )
		self._file.write( json.dumps( data ) )
		self._file.write( '\n' )
		self._file.flush( )
		self._currentWriteCount += 1
	
	def _maybeRotate( self ):
		if self._currentWriteCount >= self.MAX_RECORDS_PER_FILE:
			self._doRotate( )
	
	def _doRotate( self ):
		if self._file is not None:
			self._file.flush( )
			self._file.close( )
			self._file = None
		
		# clean up existing journal file
		if os.path.exists( self._currentPath ):
			newFile = os.path.join( self._completePath, 'blob-' + str(time.time()) )
			os.rename( self._currentPath, newFile )
		
		self._currentWriteCount = 0
		self._file = open( self._currentPath, 'wa' )

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
			metricJournals.writeData( metrics )

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
