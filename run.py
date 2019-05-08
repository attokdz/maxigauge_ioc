import logging
from argparse import ArgumentParser
import sys
from pcaspy import SimpleServer
from pcaspy.tools import ServerThread
import ioc
from maxigauge import maxigauge


parser = ArgumentParser()
parser.add_argument("ioc_prefix", type=str, help="Prefix of the IOC.")
parser.add_argument("--serial", type=str, help="Serial port")
parser.add_argument("--log_level", default="WARNING", choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'], help="Log level to use.")
arguments = parser.parse_args()
logging.basicConfig(stream=sys.stdout, level=arguments.log_level)
_logger = logging.getLogger(arguments.ioc_prefix)
_logger.info("Starting ioc with prefix '%s", arguments.ioc_prefix)

maxi=maxigauge(arguments.serial)
maxi.loadSensors()
_logger.info("I got %d sensors in the controller."%maxi._NumSensors)

prefixs=[]
pvsGauge={}
pvsRelay={}

for j in range(len(maxi.sensors)):
	prefixs.append("PG%d"%j)
	pvsGauge.update(ioc.pvsPG(prefixs[-1]))
	
for j in range(len(maxi.relay)):
	prefixs.append("RL%d"%j)
	pvsRelay.update(ioc.pvsRELAY(prefixs[-1]))

server = SimpleServer()
server.createPV(prefix=arguments.ioc_prefix, pvdb=pvsGauge)
server.createPV(prefix=arguments.ioc_prefix, pvdb=pvsRelay)

driver = ioc.maxigauge_ioc(maxi, prefixs)
server_thread = ServerThread(server)
server_thread.start()

if __name__ == "__main__":
	while not(input("Press 'q' to quit: ")=='q'):
		pass
	_logger.info("User requested ioc termination. Exiting.")
	server_thread.stop()
	sys.exit()
	

	
	
