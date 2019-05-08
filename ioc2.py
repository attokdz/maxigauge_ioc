"""
#---------------------------------------------------------#
| Author: Fernando Ardana-Lamas                           |
| Affilation: ETH Zurich                                  |
| Description: IOC for running Maxigauge controllers .    |
| Version: 1.0 b - 2015-05-17                             |
#---------------------------------------------------------#
"""


import logging
from pcaspy import  Driver
logger = logging.getLogger("__name__")




def pvsPG(prefix):
	pvdb={
			'%s.PRESSURE'%prefix :{ 'type': 'float', 'unit': 'mbar', 'prec': 4},
			'%s.STATUS'%prefix :{ 'type': 'enum',  'enums': ['OK', 'UNDERRANGE', 'OVERRANGE', 'ERROR', 'OFF', 'NOSENSOR','ERROR2']},
			'%s.NAME'%prefix :{ 'type': 'string'},
			'%s.TYPE'%prefix :{ 'type': 'char', 'count': 3},
			'%s.ONOFF'%prefix :{ 'type': 'enum', 'enums': ['ON', 'OFF']},
			}
			
	return pvdb
			
def pvsRELAY(prefix):
	pvdb={
			'%s.SENSOR'%prefix :{ 'type': 'int', 'unit': '-'},
			'%s.LOWER'%prefix :{ 'type': 'float', 'unit': 'mbar'},
			'%s.UPPER'%prefix :{ 'type': 'float', 'unit': 'mbar'},
			}
			
	return pvdb
			


class maxigauge_ioc:

	def __init__(self, driver, prefix, prefixs, parent):
		self.driver=driver
		self.prefix=prefix
		self.parent=parent
		self.ready=False
		if not(len(prefixs)==12):
			logger.exception("Not enough channels.")
			return
		
		self._prefixs=prefixs
		for i in range(6):
			self.setParam("%s.PRESSURE"%self._prefixs[i], self.driver.pressures[i])
			self.setParam("%s.STATUS"%self._prefixs[i], self.driver.status[i])
			self.setParam("%s.NAME"%self._prefixs[i], self.driver.names[i])
			print(self.driver.names[i])
			self.setParam("%s.TYPE"%self._prefixs[i], self.driver.types[i])
		for i in range(6,12):
			self.setParam("%s.SENSOR"%self._prefixs[i], int(self.driver.relay[i-6][0]))
			self.setParam("%s.LOWER"%self._prefixs[i], float(self.driver.relay[i-6][1]))
			self.setParam("%s.UPPER"%self._prefixs[i], float(self.driver.relay[i-6][2]))
		self.setParam("Status", True)

		
		
		
	def update(self):
		self.driver.updateSensors()
		for i in range(6):
			self.updateSensor(i)

	def read(self, reason):		
		return self.getParam(reason)
			
		
		
	def write(self, reason, value):
		prefix=reason.split(".")
		try:
			index=self._prefixs.index(prefix[0])
		except:
			logger.exception("ERROR Setting PV.")
			return
		
		if index<6:
			if prefix[1]=="NAME":
				if self.driver.setName(index+1, value):
					logger.exception("ERROR setting gauge name.")
					return
				self.setParam(reason, self.driver.names[index].encode())
				
			if prefix[1]=="ONOFF":
				if value==1:
					if self.driver.switchON(index+1):
						logger.exception("ERROR turning on gauge.")
						return 
				elif value==0:
					if self.driver.switchOFF(index+1):
						logger.exception("ERROR turning off gauge.")
						return 
				
				self.setParam(reason, value)

			else:
				self.setParam(reason, value)
			
				
		elif index>6:
			if prefix[1]=="SENSOR":
				if self.driver.setRelay(index-5, value, self.relay[index-6][1], self.relay[index-6][2]):
					logger.exception("ERROR setting relay sensor.")
					return
					
				self.setParam(reason, self.driver.name[index-6].encode())
					
			elif prefix[1]=="LOWER":
				if self.driver.setRelay(index-5, self.relay[index-6][0], value, self.relay[index-6][2]):
					logger.exception("ERROR setting relay sensor.")
					return
				self.setParam(reason, self.driver.name[index-6])
			else:
				self.setParam(reason, value)
	
		return self.getParam(reason)

	def getParam(self, reason):
		return self.parent.getParam("%s:%s"%(self.prefix, reason))
	
	def setParam(self, reason, value):
		return self.parent.setParam("%s:%s"%(self.prefix, reason), value)

	def updatePVs(self):
		self.parent.updatePVs()
		
	def updateSensor(self, i):
		self.setParam("%s.PRESSURE"%(self._prefixs[i]), self.driver.pressures[i])
		self.setParam("%s.STATUS"%(self._prefixs[i]), self.driver.status[i])

		
	
