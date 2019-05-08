"""
#---------------------------------------------------------#
| Author: Fernando Ardana-Lamas                           |
| Affilation: ETH Zurich                                  |
| Description: Driver for Maxigauge controllers .         |
| Version: 1.0 b - 2015-05-17                             |
#---------------------------------------------------------#
"""



from serial import Serial
import logging

logger = logging.getLogger("__name__")

ack="%s\r\n"%chr(6)
nak="%s\r\n"%chr(21)
enq="%s\r\n"%chr(5)

def dummy(i):
	pass

class Sensor():

	def __init__(self, index, sendAndRead, state=0, pressure=0):
		self.sendAndRead=sendAndRead
		self._ix=index
		self._state=state
		self._pressure=pressure
		
		
	def getPressure(self):
		res=self.sendAndRead("PR%d"%self._ix)
		if not(res):
			logger.ERROR("Error reading sensor status")
			return True
		res=res[:-2].split(",")
		self._pressure=float(res[1])
		self._state=int(res[0])		
		return False
	
	def switchOFF(self):
		val=[0,0,0,0,0,0]
		val[self._ix-1]=1
		str="SEN"
		for i in val:
			str+=",%d"%i
		return str
		
	def switchON(self):
		val=[0,0,0,0,0,0]
		val[self._ix-1]=2
		str="SEN"
		for i in val:
			str+=",%d"%i
		return str
		
		
		
	

class maxigauge():

	def __init__(self, port, baudrate=9600):
		self._port=port
		self._baudrate=baudrate
		self.ready=False
		self.sensorCB=dummy

		try:
			self._sh=Serial(self._port, self._baudrate)
		except:
			logger.ERROR("Error connecting to serial port")
			return 		
		self._ready=True
		return
	
	
	def loadSensors(self):
		self.sensors=[]
		self.status=[]
		self.pressures=[]
		self.getNames()
		self.getTypes()
		self.getRelais()
				
		for i in range(1,7):
			resp=self.sendAndRead("PR%d"%i)
			resp=resp[:-2].split(",")
			pr=float(resp[1])
			st=int(resp[0])
			self.sensors.append(i)
			self.status.append(st)
			self.pressures.append(pr)
		self._NumSensors=len(self.sensors)-1

		
	def getNames(self):
		res=self.sendAndRead("CID")
		if not(res):
			logger.exception("Error retriving sensor names")
			return True
		self.names=res[:-2].split(",")
		return False
		
		
	def setName(self, index, name):
		if len(name)>4:
			print("Name too long")
			return True
		self.names[index-1]=name
		cmd="CID"
		for i in self.names:
			cmd+=",%s"%i
		res=self.sendAndRead(cmd)
		if not(res):
			logger.exception("Error setting sensor names")
			return True
		self.names=res[:-2].split(",")
		return False
		
		
	def getTypes(self):
		res=self.sendAndRead("TID")
		if not(res):
			logger.exception("Error retriving sensor names")
			return True
		self.types=res[:-2].split(",")
		return False
		
	def getRelais(self):
		self.relay=[]
		for i in range(1,7):
			self.relay.append([])
			self.getRelay(i)
		return False
		
	def getRelay(self, index):
		res=self.sendAndRead("SP%d"%index)
		if not(res):
			logger.exception("error retreaving switcher %d."%i)
			return True
		res=res[:-2].split(",")
		self.relay[index-1]=res
		return False
		
	def setRelay(self, index, sensor, lo, up):
		cmd="SP%d,%d,%.2E,%.2E"%(index,sensor-1,lo,up)		
		res=self.sendAndRead(cmd)
		if not(res):
				logger.exception("error setting switcher %d."%i)
				return True
		self.relay[index-1]=res
		return False
		
		
		
	def switchOFF(self, sensNr):
		for j in range(self._NumSensors):
			if self.sensors[j]==sensNr:
				break

		val=[0,0,0,0,0,0]
		val[sensNr-1]=1
		str="SEN"
		for i in val:
			str+=",%d"%i		
		res=self.sendAndRead(str)
		if not(res):
			logger.exception("Error switching OFF sensor, can be switched?")
			return True
		self.updateSensor(j)
				

	def switchON(self, sensNr):
		for j in range(self._NumSensors):
			if self.sensors[j]==sensNr:
				break
		val=[0,0,0,0,0,0]
		val[sensNr-1]=2
		str="SEN"
		for i in val:
			str+=",%d"%i		
		res=self.sendAndRead(str)
		if not(res):
			logger.exception("Error switching ON sensor, can be switched?")
			return True
		self.updateSensor(j)		
	
	def sendAndRead(self, cmd):
		self._sh.write(("%s\r\n"%cmd).encode())
		o=self._sh.readline().decode()
		if not(o==ack):
			logger.exception("Error sending command")
			return False
		self._sh.write(enq.encode())
		return self._sh.readline().decode()
		
	def updateSensors(self):
		for i in range(self._NumSensors):
			if self.updateSensor(i):
				logger.exception("Error updating sensor %d"%self.sensors[i])
				return True
		return False
			
	def updateSensor(self, i):
		res=self.sendAndRead("PR%d"%self.sensors[i])
		if not(res):
			logger.exception("Error reading sensor %d."%self.sensors[i])
			return True
		res=res[:-2].split(",")
		self.status[i]=int(res[0])
		self.pressures[i]=float(res[1])
		self.sensorCB(i)
		return False

			
			
		
		
		

		
