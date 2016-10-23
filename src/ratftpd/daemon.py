import sys, os, time, atexit
import logging
import os.path
import os
from signal import SIGTERM
 
logger = logging.getLogger(__name__)
class Daemon(object):
    """
    A generic daemon class.
       
    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null', uid=os.getuid(), gid=os.getgid()):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = os.path.abspath(pidfile)
        self.uid = uid
        self.gid = gid
 
    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                os._exit(0)
        except OSError as e:
            logger.error("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            os._exit(1)
       
        logger.debug("first fork ok")
        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)
       
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                os._exit(0)
        except OSError as e:
            logger.error("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            os._exit(1)
        logger.debug("second fork ok")

        # redirect standard open descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(self.stdin, 'r')
        so = open(self.stdout, 'a+')
        se = open(self.stderr, 'ab+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        logger.debug("close fd")
       
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)
        
    def delpid(self):
        os.remove(self.pidfile)
 
    def dropPrivilege(self):
        if os.getuid() != 0:
            return
        if os.getgid() != self.gid:
            os.setgid(self.gid)
        if os.getuid() != self.uid:
            os.setuid(self.uid)

    def start(self):
        """
        Start the daemon
        """
        logger.info("start daemon")
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            os._exit(1)
           
        # Start the daemon
        self.daemonize()
 
    def stop(self):
        """
        Stop the daemon
        """
        logger.info("stop process")
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None
       
        if not pid:
            message = "pidfile %s does not exist. Daemon not running?"
            logger.info(message)
            return # not an error in a restart
 
        # Try killing the daemon process       
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    logger.debug("remove pid file")
                    os.remove(self.pidfile)
            else:
                print(str(err))
                os._exit(1)
