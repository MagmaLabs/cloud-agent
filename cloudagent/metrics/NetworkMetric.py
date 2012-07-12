from cloudagent.Metric import Metric

import os.path

class NetworkMetric(Metric):
	def __init__( self ):
		pass
	
	def getInterval( self ):
		return (5*60)
	
	def supported( self ):
		return os.path.exists( '/proc/meminfo' )
	
	def getMetrics( self ):
		lines = open("/proc/net/dev", "r").readlines()

		columnLine = lines[1]
		_, receiveCols , transmitCols = columnLine.split("|")
		receiveCols = map(lambda a:"rx_"+a, receiveCols.split())
		transmitCols = map(lambda a:"tx_"+a, transmitCols.split())

		cols = receiveCols+transmitCols

		faces = {}
		for line in lines[2:]:
		    if line.find(":") < 0: continue
		    face, data = line.split(":")
		    faceData = dict(zip(cols, [int(a) for a in data.split()]))
		    faces[face.strip(' ')] = faceData

		networkData = {}
		for iface, stats in faces.iteritems():
			networkData[iface] = {
				'rx_bytes': stats['rx_bytes'],
				'tx_bytes': stats['tx_bytes'],
				
				'rx_packets': stats['rx_packets'],
				'tx_packets': stats['tx_packets'],
			}

		return {
			'type': 'network',
			'data': {
				'network': networkData,
			}
		}