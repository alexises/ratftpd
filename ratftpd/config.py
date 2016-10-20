from ipaddress import ip_network
from functools import cmp_to_key

class Config(object):
    ''' manage configuration '''

    def __init__(self, config):
        self.bind = config.get("bind", "")
        self.port = config.get("port", 69)
        self.timeout = config.get("timeout", 5)
        self.retry = config.get("retry", 5)
        networks = []
        for network in config.get('networks', []):
            networks.append(NetworkConfig(self, network))
        self._sortNetwork(networks, config)

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
        self.networks.makeTree()
        

class NetworkConfig(object):
    ''' manage a configuration for a network '''

    def __init__(self, parent, config):
        self.timeout = config.get('timeout', parent.timeout)
        self.retry = config.get('retry', parent.retry)
        if 'network' not in config:
            raise ValueError('network argument is required for a network entry')
        self.network = ip_network(config['network'])
        self.subnets = []

    def addChild(self, child):
        self.subnets.append(child)

    def makeTree(self):
        refIndex = 0
        currentIndex = 1
        networks = self.subnets
        self.subnets = []
        for i in range(1, len(networks)):
            if networks[refIndex].network.overlaps(
                 networks[currentIndex].network
               ):
                networks[refIndex].addChild(networks[currentIndex])
                currentIndex += 1
            else:
                self.subnets.append(networks[refIndex])
                networks[refIndex].makeTree()
                refIndex = currentIndex
                currentIndex += 1
            if currentIndex >= len(networks) or refIndex >= len(networks):
                break

        if refIndex < len(networks):
           self.subnets.append(networks[refIndex])
           networks[refIndex].makeTree()
        

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
        print("{0} {1} {2}".format("-" * level, str(self.network), len(self.subnets)))
        for subnet in self.subnets:
            subnet.pretyPrint(level+4)
