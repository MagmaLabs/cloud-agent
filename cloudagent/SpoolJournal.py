import os
import time
try:
	import simplejson as json
except ImportError:
	import json

class SpoolJournal(object):
	MAX_RECORDS_PER_FILE = 1000
	MAX_SECONDS_PER_FILE = (5*60)
	
	def __init__( self, path ):
		self._filePath = path
		
		self._currentPath = os.path.join( path, 'current' )
		self._completePath = os.path.join( path, 'complete' )
		
		if not os.path.exists( self._completePath ):
			os.makedirs( self._completePath )
		
		self._file = None
		self._doRotate( )
	
	def writeData( self, data ):
		self._file.write( json.dumps( data ) )
		self._file.write( '\n' )
		self._file.flush( )
		self._currentWriteCount += 1
		self._maybeRotate( )
	
	def _maybeRotate( self ):
		if self._currentWriteCount >= self.MAX_RECORDS_PER_FILE or self._firstWrite + self.MAX_SECONDS_PER_FILE < time.time():
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
		self._firstWrite = time.time( )
		self._file = open( self._currentPath, 'wa' )