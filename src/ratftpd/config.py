# This file is part of Ratftpd.
#
# Ratftpd is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ratftpd is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ratftpd.  If not, see <http://www.gnu.org/licenses/>.

from ipaddress import ip_network, ip_address
from functools import cmp_to_key
import logging
from threading import Lock
import os.path
import os
import pwd
import grp

logger = logging.getLogger(__name__)
class Config(object):
    ''' manage configuration '''

    def __init__(self, config):
        self.bind = config.get("bind", "")
        self.port = config.get("port", 69)
        self.timeout = config.get("timeout", 5)
        self.retry = config.get("retry", 5)
        self.pidfile = config.get("pidfile", "ratftpd.pid")
        self.maxConn = config.get("maxConn", 65535)
        self.blksize = config.get("blksize", None)
        self.basepath = os.path.abspath(config.get("basepath", "tftproot"))
        self.pathalias = config.get("pathalias", {})
        self.uid = pwd.getpwnam(config.get("user", pwd.getpwuid(os.getuid()).pw_name)).pw_uid
        self.gid = grp.getgrnam(config.get("group", grp.getgrgid(os.getgid()).gr_name)).gr_gid

        for alias in self.pathalias:
            self.pathalias[alias] = os.path.join(self.basepath, self.pathAlias[alias])

        networks = []
        for network in config.get('networks', []):
            networks.append(NetworkConfig(self, network))
        self._sortNetwork(networks, config)
        logger.info("load config")

    def _sortNetwork(self, networks, config):
        networks.sort()        
        if networks[0].network.prefixlen == 0:
           network = network[0]
        else:
           configCpy = dict(config)
           configCpy['network'] = '0.0.0.0/0'
           network = NetworkConfig(self,  configCpy)
           networks.insert(0, network)
        self.networks = network
        for network in networks[1:]:
            self.networks.addChild(network)
        self.networks.makeTree(self)

    def getConfig(self, ip):
        ip_subnet = ip_address(ip)
        config = self.networks
        while config.subnets:
            for subnet in config.subnets:
                if subnet.network.overlaps(ip_subnet):
                    config = subnet
                    break
            else:
                break
        return config
                    

class NoSlotAvailable(Exception):
    def __init__(self, network, childs):
        super().__init__("max number of connexion for {0}".format(network))
        self.network = network
        self.childs = childs

class NetworkConfig(object):
    ''' manage a configuration for a network '''

    def __init__(self, parent, config):
        if 'network' not in config:
            raise ValueError('network argument is required for a network entry')
        self.network = ip_network(config['network'])
        self.subnets = []
        if 'basepath' in config:
            self.basepath = config['basepath']
        elif 'alias' in config:
            if config['alias'] not in parent.pathalias:
               raise ValueError("alias {} not present".format(config['alias']))
            self.basepath = parent.pathalias(config['alias'])
        else:
            self.basepath = parent.basepath
        self._config = config
        self._connLock = Lock()

    def _setConfig(self):
        self.timeout = self._config.get('timeout', self.parent.timeout)
        self.retry = self._config.get('retry', self.parent.retry)
        self.maxConn = self._config.get('maxConn', self.parent.maxConn)
        self.blksize = self._config.get('blksize', self.parent.blksize)
        del self._config

    def addChild(self, child):
        self.subnets.append(child)

    def addConnection(self):
        subnets = []
        elem = self
        while elem != None:
            subnets.append(elem)
            elem._connLock.acquire()
            if elem.maxConn > 0:
                logger.debug("nex slot avaliable for {} network is {}".format(elem.network, elem.maxConn))
            else:
                logger.error("max number of connection reached")
                for subnet in subnets:
                    subnet._connLock.release()
                raise NoSlotAvailable(elem, subnets)
            elem = elem.parent
        logger.info("max connection countion downgraded")
        for subnet in subnets:
            subnet.maxConn -= 1
            elem._connLock.release()

    def delConnection(self):
        elem = self
        while elem != None:
            with elem._connLock:
                elem.maxConn +=1
            elem = elem.parent

    def makeTree(self, parent):
        refIndex = 0
        currentIndex = 1
        networks = self.subnets
        self.subnets = []
        self.parent = parent
        self._setConfig()
        for i in range(1, len(networks)):
            if networks[refIndex].network.overlaps(
                 networks[currentIndex].network
               ):
                networks[refIndex].addChild(networks[currentIndex])
                currentIndex += 1
            else:
                self.subnets.append(networks[refIndex])
                networks[refIndex].makeTree(self)
                refIndex = currentIndex
                currentIndex += 1
            if currentIndex >= len(networks) or refIndex >= len(networks):
                break

        if refIndex < len(networks):
           self.subnets.append(networks[refIndex])
           networks[refIndex].makeTree(self)

    def _getNumeric(self, other):
        cmpVal = self.network.compare_networks(other.network)
        if not cmpVal:
            return self.network.prefixlen - other.network.prefixlen
        return cmpVal

    def __lt__(self, other):
        return self._getNumeric(other) < 0

    def __gt__(self, other):
        return self._getNumeric(other) > 0

    def __eq__(self, other):
        return self._getNumeric(other) == 0

    def __le__(self, other):
        return self._getNumeric(other) <= 0

    def __ge__(self, other):
        return self._getNumeric(other) >= 0

    def __ne__(self, other):
        return self._getNumeric(other) != 0

    def pretyPrint(self, level=0):
        logger.info("{0} {1} {2}".format("-" * level, str(self.network), len(self.subnets)))
        for subnet in self.subnets:
            subnet.pretyPrint(level+4)
