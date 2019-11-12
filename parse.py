import sys, os, signal
import time, datetime
import re
import requests
import getopt

# Defaults
responseCodePosition = 5
datePosition         = 3

# Initialize
logFile         = ''
startTime       = ''
endTime         = ''
eventCount      = 0
responseCounts  = [0 for i in range(6)]
responsePercent = [0 for i in range(6)]
oldestEvent     = 0
newestEvent     = 0
isLocalFile     = False

# Define signal handler
def handler(signum = None, frame = None):
    print('Exiting')
    exit(1)

# Exit signal handler
for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, handler)

# Get input parameters
options, remainder = getopt.getopt(sys.argv[1:], 's:e:l:', ['start-time=', 'end-time=','log='])
for opt, arg in options:
  if opt in ('-s', '--start-time'):
    startTime = time.mktime(datetime.datetime.strptime(arg,"%d/%b/%Y:%H:%M:%S %z").timetuple())
  elif opt in ('-e', '--end-time'):
    endTime = time.mktime(datetime.datetime.strptime(arg,"%d/%b/%Y:%H:%M:%S %z").timetuple())
  elif opt in ('-l', '--log'):
    logFile = arg

# Validate
if '' == logFile:
  print('Log file missing')
  exit(1)
if '' == startTime:
  print('Start date/time missing')
  exit(2)
if '' == endTime:
  print('End date/time missing')
  exit(3)

# Use a URL instead of a local logfile
if 'http' == logFile[:4]:
  isLocalFile = True
  url=logFile
  logFile = 'log.txt'
  try:
    with open(logFile, 'w+') as f:
      r = requests.get(url, data=f)
      f.write(r.text)
  except:
    print('Failed to get log. Exiting.')
    exit(4)

# Open log file
try:
  logObj = open(logFile, 'r')
except:
  print('File '+logFile+' does not exist')
  exit(5)

# Iterate through the log file
for logRowCount, logRow in enumerate(logObj):
  # Convert to list
  i = list(map(''.join, re.findall(r'\"(.*?)\"|\[(.*?)\]|(\S+)', logRow)))

  # Get timestamp for this event
  eventTimeStamp = time.mktime(datetime.datetime.strptime(i[datePosition],"%d/%b/%Y:%H:%M:%S %z").timetuple())

  # Skip this event if it is not within range
  if not startTime <= eventTimeStamp <= endTime:
    continue

  # Increment the event count
  eventCount += 1

  # Increment the response count
  responseCounts[int(i[responseCodePosition][:1])] += 1

  # Determine the real range of event times
  if newestEvent < eventTimeStamp:
    newestEvent = eventTimeStamp
  if oldestEvent > eventTimeStamp or 1==eventCount:
    oldestEvent = eventTimeStamp

# Calculate response percentages
for x in range(1,len(responseCounts)):
  responsePercent[x] = round(responseCounts[x] / eventCount * 100)

# Print output
print('The site has returned a total of '+str(responseCounts[2])+' 2xx responses, '+str(responseCounts[3])+' 3xx responses, '+str(responseCounts[4])+' 4xx responses, and '+str(responseCounts[5])+' 5xx responses, out of total '+str(eventCount)+' requests between '+time.ctime(oldestEvent)+' and '+time.ctime(newestEvent))
print('That is '+str(responsePercent[4])+'% 4xx errors, '+str(responsePercent[5])+'% 5xx errors, '+str(responsePercent[3])+'% 3xx redirects, and '+str(responsePercent[2])+'% 2xx responses.')

# Clean up
if isLocalFile:
  os.remove(logFile)
