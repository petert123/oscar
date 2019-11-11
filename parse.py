import sys, os, signal
import re
import time, datetime
import requests

# Defaults
sampleLogUrl         = 'https://raw.githubusercontent.com/elastic/examples/master/Common%20Data%20Formats/nginx_logs/nginx_logs'
responseCodePosition = 5
datePosition         = 3

# Initialize
logFile         = ''
successCount    = 0
responseCounts  = [0 for i in range(6)]
responsePercent = [0 for i in range(6)]
oldestEvent     = 0
newestEvent     = 0
useExample      = False

def handler(signum = None, frame = None):
    print('Exiting')
    exit(1)

# Exit signal handler
for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
    signal.signal(sig, handler)

# Use log file passed in as an argument
try:
  logFile = sys.argv[1]
except:
  noop=0 # No Op  

# Download and use example if no log provided
if '' == logFile:
  print('No logfile provided. Using example')
  useExample = True
  try:
    logFile = 'log.txt'
    with open(logFile, 'w+') as f:
      r = requests.get(sampleLogUrl, data=f)
      f.write(r.text)
  except:
    print('Failed to get example log. Exiting.')
    exit(2)

# Open log file
try:
  logObj = open(logFile, 'r')
except:
  print('File '+logFile+' does not exist')
  exit(3)

# Count rows in the log file
for logRowCount, logRow in enumerate(logObj):
  # Convert to list
  i = list(map(''.join, re.findall(r'\"(.*?)\"|\[(.*?)\]|(\S+)', logRow)))

  # Iterate the response count
  responseCounts[int(i[responseCodePosition][:1])] += 1

  # Get timestamp for this event
  eventTimeStamp = time.mktime(datetime.datetime.strptime(i[datePosition],"%d/%b/%Y:%H:%M:%S %z").timetuple())

  # Determine the range of event times
  if newestEvent < eventTimeStamp:
    newestEvent = eventTimeStamp
  if oldestEvent > eventTimeStamp or logRowCount==0:
    oldestEvent = eventTimeStamp

# Iterate the row count since it started at 0
logRowCount += 1

# Calculate response percentages
for x in range(1,len(responseCounts)):
  responsePercent[x] = round(responseCounts[x] / logRowCount * 100)

# Print output
print('The site has returned a total of '+str(responseCounts[2])+' 2xx responses, '+str(responseCounts[3])+' 3xx responses, '+str(responseCounts[4])+' 4xx responses, and '+str(responseCounts[5])+' 5xx responses, out of total '+str(logRowCount)+' requests between '+time.ctime(oldestEvent)+' and '+time.ctime(newestEvent))
print('That is '+str(responsePercent[4])+'% 4xx errors, '+str(responsePercent[5])+'% 5xx errors, '+str(responsePercent[3])+'% 3xx redirects, and '+str(responsePercent[2])+'% 2xx responses.')

# Clean up
if useExample:
  os.remove(logFile)
