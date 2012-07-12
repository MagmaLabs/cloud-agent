from ..Metric import Metric

class MemoryMetric(Metric):
	def __init__( self ):
		pass
	
	def getInterval( self ):
		return (5*60)
	
	def getMetrics( self ):
		memoryData = open('/proc/meminfo').read()

		meminfo = {}
		for line in memoryData.strip().split('\n'):
			data = line.strip().split()
			name = data[0].strip(':')
			value = int(data[1])
			meminfo[name] = value

		return {
			'type': 'memory',
			'data': {
				'memory': {
					'physical': {
						'free': meminfo['MemFree'],
						'buffers': meminfo['Buffers'],
						'cached': meminfo['Cached'],
						'used': meminfo['MemTotal'] - ( meminfo['MemFree'] + meminfo['Cached'] + meminfo['Buffers'] ),
						'total': meminfo['MemTotal'],
					},
					'swap': {
						'free': meminfo['SwapFree'],
						'cached': meminfo['SwapCached'],
						'used': meminfo['SwapTotal'] - ( meminfo['SwapFree'] + meminfo['SwapCached'] ),
						'total': meminfo['SwapTotal'],
					}
				}
			}
		}