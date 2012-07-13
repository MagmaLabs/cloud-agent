from twisted.internet import reactor
from twisted.internet import defer
from twisted.web import client
from twisted.web.http_headers import Headers
from twisted.application.service import Service

from cloudagent.twistedExtensions.MultiPartProducer import MultiPartProducer
from cloudagent.MetricService import MetricService, METRICS_SPOOL_DIR

import os

import agent_settings

class PushService(Service):
	PUSH_DELAY_SUCCESS = 5
	PUSH_DELAY_POLL = 60
	PUSH_DELAY_ERROR = (5*60) # when an error occurs, wait 5 minutes before retrying
	
	def __init__( self ):
		self._completeDir = METRICS_SPOOL_DIR + '/complete'
	
	def startService( self ):
		Service.startService( self )
		print 'started push service'
		
		self._queuePoll( 0 )

	def stopService( self ):
		print 'stopped push service'
		Service.stopService( self )
	
	def _pollPush( self ):
		didPush = False
		
		if os.path.exists( self._completeDir ):
			files = os.listdir( self._completeDir )
			if len(files) > 0:
				targetFile = files[0]
			
				didPush = True
				self._doPush( os.path.join( self._completeDir, targetFile ) )
		
		if not didPush:
			self._queuePoll( )
	
	def _queuePoll( self, secondsAway=None ):
		if secondsAway is None:
			secondsAway = self.PUSH_DELAY_POLL
		reactor.callLater( secondsAway, self._pollPush )
	
	def _finished( self, bytes ):
		print 'Upload done', bytes

	def _error( self, error ):
		print 'Upload error in push service, waiting %d seconds before retrying' % self.PUSH_DELAY_ERROR
		print error
		self._queuePoll( self.PUSH_DELAY_ERROR )

	def _progress( self, current, total ):
		print 'Upload progress', current, 'out of', total

	def _responseReady( self, response, filename ):
		if response.code == 200:
			# success, remove the file, it's pushed!
			print 'success! removing file:', filename
			os.unlink( filename )
			
			# now queue another file for pushing
			self._queuePoll( self.PUSH_DELAY_SUCCESS )
		else:
			# error while uploading :(
			print 'Upload error in push service, received response %d %s from server (expected 200 OK)' % (response.code, response.phrase)
			self._queuePoll( self.PUSH_DELAY_ERROR )

	def _doPush( self, filename ):
		print 'beginning push of file:', filename
		producerDeferred = defer.Deferred()
		producerDeferred.addCallback( self._finished )
		producerDeferred.addErrback( self._error )
		
		multiPartProducer = MultiPartProducer(
			files={
				'metrics': filename,
			},
			data={
				'secret': agent_settings.PUSH_DETAILS['secret'],
			},
			callback=self._progress,
			deferred=producerDeferred
		)
	
		headers = Headers()
		headers.addRawHeader( 'Content-Type', 'multipart/form-data; boundary=%s' % multiPartProducer.boundary )
	
		agent = client.Agent( reactor )
		request = agent.request(
			'POST',
			agent_settings.PUSH_DETAILS['url'],
			headers,
			multiPartProducer
		)
		request.addCallback( self._responseReady, filename )
