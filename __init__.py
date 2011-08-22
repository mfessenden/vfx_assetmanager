import sys

__dependencies__ = 'pyqt'

# determine with application is running
app = sys.executable.split('\\')[len(sys.executable.split('\\'))-1]
if app.startswith('maya'):
    print '[AM2]: loading Maya libraries...'
    
    
if app.startswith('Nuke'):
    print '[AM2]: loading Nuke libraries...'
