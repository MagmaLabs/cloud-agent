import os
from string import uppercase
from warnings import warn

def importAllSubclassing( importPath, superClass ):
	importedClasses = []
	for importedClass in importAll(importPath):
		if issubclass(importedClass, superClass):
			importedClasses.append( importedClass )
		else:
			warn( "'%s' does not subclass %s." % (importedClass.__name__, superClass.__name__) )
	return importedClasses

def importAll( importPath ):
	directory = _getPathForImportPath( importPath )
	importedClasses = []

	for dirname, dirnames, filenames in os.walk( directory ):
		for filename in filenames:
			# only looks at files starting with uppercase letters
			if filename.endswith( ".py" ) and filename[0] in uppercase:
				className = filename[:-3]
				subpath = os.path.join( dirname, filename )[len(directory):]
				importName = subpath[:-3].replace( os.path.sep, '.' ).strip(".")
				fullImportName = importPath + '.' + importName

				try:
					importedModule = __import__(fullImportName, globals(), locals(), [className])
				except ImportError as e:
					print ( "While importing '%s' from '%s': %s" % (className, importName, e.args[0]) )
				else:
					if hasattr(importedModule, className):
						importedClass = getattr(importedModule, className)
						importedClasses.append( importedClass )
					else:
						print ( "Couldn't import '%s' from '%s'." % (className, importName) )
	return importedClasses
	
def _getPathForImportPath( importPath ):
	baseModule = __import__(importPath)
	for part in importPath.split( '.' )[1:]:
		baseModule = getattr( baseModule, part )
	return os.path.split( baseModule.__file__ )[0]