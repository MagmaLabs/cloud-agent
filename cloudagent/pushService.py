from twisted.internet import reactor
from twisted.internet import defer
from twisted.web import client
from twisted.web.http_headers import Headers

from cloudagent.twistedExtensions.MultiPartProducer import MultiPartProducer

import agent_settings

def finished(bytes):
	print 'Upload done', bytes

def error(error):
	print 'Upload error', error

def progress( current, total ):
	print 'Upload progress', current, 'out of', total

def responseReady( response ):
	print 'got response', response

def doPush( filename ):
	producerDeferred = defer.Deferred()
	producerDeferred.addCallback(finished)
	producerDeferred.addErrback(error)
	
	
	multiPartProducer = MultiPartProducer(
		files={
			"upload": "/home/mariano/myfile.tar.gz"
		},
		data={
			"field1": "value1"
		},
		callback=progress,
		deferred=producerDeferred
	)
	
	headers = Headers()
	headers.addRawHeader( 'Content-Type', 'multipart/form-data; boundary=%s' % multiPart.boundary )
	
	agent = client.Agent( reactor )
	request = agent.request(
		'POST',
		agent_settings.PUSH_DETAILS['url'],
		headers,
		multiPartProducer
	)
	request.addCallback( responseReady )
