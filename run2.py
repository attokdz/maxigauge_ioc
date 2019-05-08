"""
#---------------------------------------------------------#
| Author: Fernando Ardana-Lamas                           |
| Affilation: ETH Zurich                                  |
| Description: Startup application for maxigauge ioc.     |
| Version: 1.0 b - 2018-05-17                             |
#---------------------------------------------------------#
"""



import logging
from argparse import ArgumentParser
import sys
from pcaspy import SimpleServer
from threading import Thread
import ioc_merge
import ioc2 as ioc
from maxigauge import maxigauge


class serverThread(Thread):

	def __init__(self, server, driver):
		Thread.__init__(self)
		self.server=server
		self.driver=driver
		self.keep=True

	def run(self):
		while(self.keep):
			self.driver.update()
			self.server.process(0.1)
	def stop(self):
		self.keep=False





parser = ArgumentParser()
parser.add_argument("ioc_prefix", type=str, help="Prefix of the IOC.")
parser.add_argument("--serial1", type=str, help="Serial port controller 1")
parser.add_argument("--prefix1", type=str, help="Prefix for controller 1")
parser.add_argument("--serial2", type=str, help="Serial port controller 2")
parser.add_argument("--prefix2", type=str, help="Prefix for controller 2")
parser.add_argument("--log_level", default="WARNING", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], help="Log level to use.")
arguments = parser.parse_args()


logging.basicConfig(stream=sys.stdout, level=arguments.log_level)
_logger = logging.getLogger(arguments.ioc_prefix)
_logger.info("Starting ioc with prefix '%s", arguments.ioc_prefix)

maxi=maxigauge(arguments.serial1)
maxi.loadSensors()
_logger.info("I got %d sensors in the 1st controller."%maxi._NumSensors)

maxi2=maxigauge(arguments.serial2)
maxi2.loadSensors()
_logger.info("I got %d sensors in the 2nd controller."%maxi2._NumSensors)


prefixs1=[]
pvsGauge1={}
pvsRelay1={}

for j in range(len(maxi.sensors)):
	prefixs1.append("PG%d"%(j))
	pvsGauge1.update(ioc.pvsPG( "%s:%s"%(arguments.prefix1, prefixs1[-1]) ))
	
for j in range(len(maxi.relay)):
	prefixs1.append("RL%d"%(j))
	pvsRelay1.update(ioc.pvsRELAY( "%s:%s"%(arguments.prefix1, prefixs1[-1]) ))


prefixs2=[]
pvsGauge2={}
pvsRelay2={}

for j in range(len(maxi2.sensors)):
	prefixs2.append("PG%d"%(j))
	pvsGauge2.update(ioc.pvsPG( "%s:%s"%(arguments.prefix2, prefixs2[-1]) ))
	
for j in range(len(maxi2.relay)):
	prefixs2.append("RL%d"%j)
	pvsRelay2.update(ioc.pvsRELAY( "%s:%s"%(arguments.prefix2, prefixs2[-1])))

pv1={"%s:Status"%(arguments.prefix1) : {'type': 'int', 'value' :0}}
pv2={"%s:Status"%(arguments.prefix2) : {'type': 'int', 'value' :0}}
pvdbs={}
pvdbs.update(pv1)
pvdbs.update(pv2)
pvdbs.update(pvsGauge1)
pvdbs.update(pvsRelay1)
pvdbs.update(pvsGauge2)
pvdbs.update(pvsRelay2)
#print(pv1)



server = SimpleServer()
server.createPV(prefix=arguments.ioc_prefix, pvdb=pvdbs)
#server.createPV(prefix=arguments.ioc_prefix, pvdb=pvsRelay1)
#server.createPV(prefix=arguments.ioc_prefix, pvdb=pvsGauge2)
#server.createPV(prefix=arguments.ioc_prefix, pvdb=pvsRelay2)

driver = ioc_merge.ioc()

contr1=ioc.maxigauge_ioc(maxi, arguments.prefix1, prefixs1, driver)
contr2=ioc.maxigauge_ioc(maxi2, arguments.prefix2, prefixs2, driver)

driver.add_ioc(contr1)
driver.add_ioc(contr2)

server_thread = serverThread(server, driver)
server_thread.start()




if __name__ == "__main__":
	while not(input("Press 'q' to quit: ")=='q'):
		pass
	_logger.info("User requested ioc termination. Exiting.")
	server_thread.stop()
	sys.exit()
	

	
	
