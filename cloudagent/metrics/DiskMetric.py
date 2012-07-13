from cloudagent.Metric import Metric

import subprocess
import sys
import os
import re
import plistlib

class DiskMetric(Metric):
	def __init__( self ):
		self.endfsent = None
		self.setfsent = None
		self.getfsent = None
		pass
	
	def getInterval( self ):
		return (10*60)

	def supported( self ):
		return os.path.exists( '/etc/mtab' ) or sys.platform == 'darwin'
	
	def _getDisksLinux( self ):
		mtab = [l.split( ' ' ) for l in open('/etc/mtab').read( ).strip( ).split( '\n' )]
		for ent in mtab:
			# mtab uses '\0xx' (octal) for whitespace chars and '\\' for '\'
			mountPoint = re.sub('\\\\(\\\\|0[0-9]{2})', lambda x: chr(int(x.group( 1 ), 8)) if x.group( 1 )[0]=='0' else x.group( 1 ), ent[1])
			device = ent[0]
			yield (mountPoint, device)
		
	def _getDisksOSX( self ):
		plist = subprocess.check_output(['diskutil', 'list', '-plist'])
		data = plistlib.readPlistFromString( plist )
		for disk in data['AllDisksAndPartitions']:
			for partition in disk.get( 'Partitions', [] ):
				if 'MountPoint' in partition:
					mountPoint = partition['MountPoint']
					device = '/dev/' + partition['DeviceIdentifier']
					yield (mountPoint, device)
				
	
	def getMetrics( self ):
		if os.path.exists( '/etc/mtab' ):
			mountedDevices = self._getDisksLinux( )
		else:
			mountedDevices = self._getDisksOSX( )
		
		disks = {}
		for mountPoint, device in mountedDevices:
			stats = os.statvfs( mountPoint )
			# only show mounted things which have blocks and map to devices on the file-system
			if stats.f_blocks and device.startswith( '/' ):
				disks[mountPoint] = {
					'device': device,
					'available': stats.f_bavail* stats.f_bsize,
					'used': (stats.f_blocks - stats.f_bfree) * stats.f_bsize,
					'total': stats.f_blocks * stats.f_bsize,
				}
		
		return {
			'type': 'disk',
			'data': {
				'disks': disks
			}
		}
