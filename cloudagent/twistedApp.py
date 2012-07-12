from twisted.application import service
from twisted.application.internet import TimerService

def foo( ):
	print 'poll'

application = service.Application( 'cloudagent' )

timerService = TimerService( 1, foo )
timerService.setServiceParent( application )