#!/usr/bin/env python

# This file provides a simple utility to get the task parameters 
# from the meta-data server. The data is set by the boot process

# import requests
import json
import sys
import ast
import subprocess
import signal
import time
# import ceilometerFuncs as util
import threading



# keystoneAddress = "10.0.4.3"
# ceilometerAddress = "10.0.4.3"
# meterName = 'missedDeadlines'
INITIAL_INTERVAL = 5

currentTimer = threading.Timer(INITIAL_INTERVAL,None)
exitEvent = threading.Event()
taskObjs = []
applicationModes = []
applicationIndex = 0

# # ***** Get resource ID of this VM *****
# myUUID = util.getInstanceUUID()
# meterName = meterName + "_" + myUUID

def kill_tasks():
	for index,item in enumerate(taskObjs):
		item.kill()	

def handleSIGINT(signal, frame):
	kill_tasks()
	sys.exit(0)

signal.signal(signal.SIGINT, handleSIGINT)


def changeTask():
	global applicationIndex
	# Report value
	# Authenticate
	# myToken = util.getKeystoneTokenV3(keystoneAddress)


	print "Changing Taskset"

# 	# Stop old tasks
	kill_tasks()
	time.sleep(.10)
	changeSched('Linux')
	for x in xrange(0,len(applicationModes) ):

		if applicationIndex >= len(applicationModes):
			print "Done with application!"
			exitEvent.set()
			sys.exit(0)
		applicationModes_j = json.loads(applicationModes[applicationIndex])
		print type(applicationModes_j)
		mode = applicationModes_j["Mode name"]
		newDuration = applicationModes_j["ExecTime"]
		applicationIndex = applicationIndex + 1
		print '\t',mode
		print '\t',newDuration

	# 	# Report back to nova
		# totalMissed = 1
		# newTaskPayload = {}
		# newTaskPayload['type'] = 'tasksetChange'
		# newTaskPayload['metaData'] = json.dumps(mode)
		# util.addSample(address=ceilometerAddress,meter=meterName,
		# 	value=str(totalMissed),\
		# 	resource_id=myUUID,token=myToken, metaData=newTaskPayload)

	# 	# Sleep for a bit
		time.sleep(10)

	# 	# Start new tasks
		startTasks(mode,newDuration)

# 	# Start next timer
	# currentTimer = threading.Timer(mode,changeTask)
	# currentTimer.start()


# def getTaskMeta():
# 	url = 'http://169.254.169.254/openstack/latest/meta_data.json'
# 	r = requests.get(url)
# 	return ast.literal_eval(r.json()['meta']['taskset'].strip('"'))

# def getInstanceUUID():
# 	url = 'http://169.254.169.254/openstack/latest/meta_data.json'
# 	r = requests.get(url)

# 	# print json.dumps(r.json(), sort_keys=True,indent=4, \
# 		# separators=(',', ': '))
# 	# print r.json()['uuid']
# 	return r.json()['uuid']

# def createTaskInfo(UUID,taskMeta):
# 	tasks = {}
# 	for index,task in enumerate(taskMeta[0]):
# 		taskName = UUID + '_' + str(index)
# 		tasks[taskName] = [	str(taskMeta[0][index]),
# 							str(taskMeta[1][index]),
# 							str(taskMeta[2][index])]
# 	return tasks

def changeSched(sched):
	subprocess.call(['/root/liblitmus/setsched',sched])
    
def startTasks(mode,duration):
	changeSched('GSN-EDF')
	with open('/dev/shm/vmMon/mode','w') as j_file:
		json.dump(data,j_file,indent=4)
    #argv  1. wcet(ms) 2. period(ms) 3. duration(s) 4. mode (1 for cali sar, 4 for cali kalman) 5. appName 6. size/iter

	for taskID in xrange(0,1):
			myoutput = open(str(mode), 'w')
			taskObjs.append( subprocess.Popen(["/root/liblitmus/base_task",
				str(1),
				str(1),
				mode,
				str(duration),
				'-w',
				'&'
				],stdout=myoutput)
			)
	time.sleep(10)
	subprocess.call(["/root/liblitmus/release_ts"])




if __name__ == "__main__":
	# If passed a file, we need to follow the applications
	if len(sys.argv) == 2:
		
		with open(sys.argv[1]) as inFile:
			inLines = inFile.readlines()

			for lines in inLines:
				try:
					data={}
					data["Application name"]=lines.split()[0]
					data["Mode name"]=lines.split()[1]
					data["Periods"]=[int(lines.split()[2])]
					data["ExecTime"]=[int(lines.split()[3])]

					applicationModes.append(json.dumps(data))

					
				except:
					pass
	print applicationModes
					#applicationModes.append(json.loads(lines.strip()))
	# 			except:
	# 				# Probably due to malformed file, just ignore
	# 				pass
	# 			# tempJSON = json.loads(lines.strip())
	# 			# print tempJSON
	# 			# pprint.pprint(tempJSON)

	# # print getInstanceUUID()
	# # print getTaskMeta()
	# # print createTaskInfo(getInstanceUUID(),getTaskMeta())
	# applicationModes.insert(0,{'duration':5,'taskset':getTaskMeta()})
	# applicationIndex = 0

	# print applicationModes

	changeTask()

	# # Waits for input
	# print('Press Ctrl+C to quit (Kills tasks if still running)')
	# exitEvent.wait()
	# # signal.pause()

