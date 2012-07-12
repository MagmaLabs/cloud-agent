from cloudagent.Metric import Metric

import os
import re

class DiskMetric(Metric):
	def __init__( self ):
		pass
	
	def getInterval( self ):
		return (10*60)

	def supported( self ):
		return os.path.exists( '/etc/mtab' )
	
	def getMetrics( self ):
		mtab = [l.split( ' ' ) for l in open('/etc/mtab').read( ).strip( ).split( '\n' )]
		disks = []
		for ent in mtab:
			# mtab uses '\0xx' (octal) for whitespace chars and '\\' for '\'
			path = re.sub('\\\\(\\\\|0[0-9]{2})', lambda x: chr(int(x.group( 1 ), 8)) if x.group( 1 )[0]=='0' else x.group( 1 ), ent[1])
			device = ent[0]
			stats = os.statvfs( path )
			# only show mounted things which have blocks and map to devices on the file-system
			if stats.f_blocks and device.startswith( '/' ):
				disks.append( {
					'mountPoint': path,
					'device': device,
					'available': stats.f_bavail* stats.f_bsize,
					'used': (stats.f_blocks - stats.f_bfree) * stats.f_bsize,
					'total': stats.f_blocks * stats.f_bsize,
				} )

		return {
			'type': 'disk',
			'data': {
				'disks': disks
			}
		}
