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

from fbtftp.base_server import BaseServer
from fbtftp.base_handler import BaseHandler, ResponseData
from os import stat
import os.path

def print_server_stats(stats):
    counters = stats.get_and_reset_all_counters()
    print('Server stats - every {} seconds'.format(stats.interval))
    print(counters)


class RatftpServerFile(ResponseData):
    def __init__(self, basepath, path, config):
        realpath = os.path.join(basepath, path)
        self._size = os.stat(path).st_size
        self._reader = open(path, 'rb')

    def read(self, n):
        return self._reader.read(n)

    def size(self):
        return self._size

    def close(self):
        self._reader.close()
        self.config.delConnection()

class RatftpServerHandler(BaseHandler):
    def __init__(self, server_addr, peer, path, options, config, stats_callback):
        self.config = config.getConfig(peer)
        self.path = path
        if self.config.blksize is not None and \
           'blksize' in options and \
           options['blksize'] > self.config.blksize:
            options['blksize'] = self.config.blksize
        super().__init__(server_addr, peer, path, options, stats_callback)

    def get_response_date():
        self.config.addConnection()
        return RatftpServerFile(self.config.basepath, self.path, self.config)


class RatftpServer(BaseServer):
    ''' Base tftp server class '''
    def __init__(self, bind, port, timeout, retry, config):
        self.config = config
        super().__init__(bind, port, timeout, retry, print_server_stats)

    def get_handler(self, server_addr, peer, path, options):
        return RatftpServerHandler(
            server_addr, peer, path, options, self.config,
            self._handler_stats_callback)
