#!/usr/bin/env python

import logging
import sys
import time
from paramiko import SSHClient
import paramiko


class StreamToLogger(object):
    """
   Fake file-like stream object that redirects writes to a logger instance.
   """

    def __init__(self, logger, log_level=logging.INFO):

        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):

        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())


def timeit(method):
    """
    A decorator to measure time
    :param method: A python method
    :return: Method with time measurement
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        #Logging only on DEBUG.
        logging.debug('%r (%r, %r) %2.2f sec' %
              (method.__name__, args, kw, te - ts))
        return result

    return timed


@timeit
def run_remote_command(client, command, work_dir=None):
    """
    Executes a command and return stdout and stderr
    :param client: SSHClient: a runnning ssh connection
    :param command: str: a bash command
    :param work_dir: str: A directory to start with
    :return: (str, str): Both stderr and stdout
    """

    if work_dir:
        command = "cd %s;%s" % (work_dir, command)

    stdin, stdout, stderr = client.exec_command(command)
    return stderr.read(), stdout.read()


@timeit
def create_connection():
    """
    Starts a connection to the controller host
    :return:
    """

    host = "10.200.0.127"
    user = "root"
    pwd = "oracle"
    client = SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    #Try to connect to the remote host
    try:
        client.connect(hostname=host, username=user, password=pwd, look_for_keys=False, allow_agent=False)
    except:
        print "Impossivel conectar com o controller"
        exit(3)
    return client


@timeit
def main(args):
    """
    service_state:
    service_state_type:
    service_attempt:
    hostname: Name of the host
    """

    #Standard log
    filename = '/var/log/nagios/eventhandler.log'

    # Setup logging
    logging.basicConfig(level=logging.INFO, filename=filename, format='%(asctime)s - %(name)s - %(message)s')
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, logging.INFO)
    sys.stdout = sl

    # Setup variables
    service_state, service_state_type, service_attempt, hostname, handler_name = args

    # Build an EventHandler
    ev = EventHandler(service_state, service_state_type, service_attempt, hostname, handler_name)

    # If true call the specified Event Handler
    try:
        if ev.should_call_handler():

            ev.handle()

    except Exception, e:
        print "Could not parse the EventHandler. Arguments:%s" % args
        print str(e)
        exit(2)


class EventHandler:
    @timeit
    def __init__(self, service_state, service_state_type, service_attempt, hostname,
                 handler_name, handle_state="CRITICAL", handle_on_soft_attempt=3):
        """
        :param service_state: The current state of the service ("OK", "WARNING", "UNKNOWN", or "CRITICAL").
        :param service_state_type: The state type for the current service check ("HARD" or "SOFT").
        :param service_attempt: The number of the current service check retry.
        :param hostname: The name of the host
        :param handle_state: Should run a handler on witch state, see variable service_state
        :param handle_on_soft_attempt: Should handle on witch soft attempt, if None handle only on HARD state
        :param handler_name: Name of the handler (Playbook name)
        :return:
        """

        self.service_state = service_state
        self.service_state_type = service_state_type
        self.service_attempt = service_attempt
        self.hostname = hostname
        self.handler_name = handler_name
        self.handle_state = handle_state
        self.handle_on_soft_attempt = handle_on_soft_attempt

    @timeit
    def handle(self):
        """
        Send and offer they can't refuse calling Godfather
        :return:
        """
        command = "/usr/bin/ansible-playbook /etc/ansible/playbooks/%s -l %s" \
                  % (self.handler_name, 'lb2-nrpe')

        #Setup a connection
        conn = create_connection()

        #Executes the playbook
        stdout, stderr = run_remote_command(conn, command)

        if stderr:
            print stderr
            exit(2)

        #Logging propose
        print stdout

    @timeit
    def should_call_handler(self):
        """
        Check if it should call the EventHandler
        :return:
        """

        if self.service_state_type == 'HARD':

            if self.parse_hard_attempt():
                return True

        elif self.service_state_type == 'SOFT':

            # Check if passed a number or it's using the default None
            if isinstance(self.handle_on_soft_attempt, int):

                if self.parse_soft_attempt():
                    return True

        else:
            print "Service state type:%s it's not a recognize service type" % self.service_state_type
            exit(2)

        return False

    @timeit
    def parse_state(self):
        """
        Check if the service_state should be passive of a handler call
        :return: bool
        """

        if self.service_state == self.handle_state:
            return True
        else:
            return False

    @timeit
    def parse_soft_attempt(self):
        """
        Parsing a soft attempt
        :return:
        """
        # Check if it's on the right state
        if self.parse_state():

            # Check if the soft attempt it's above the call limit
            if self.parse_attempt(self.handle_on_soft_attempt):
                return True

        return False

    @timeit
    def parse_hard_attempt(self):
        """
        Parsing a hard attempt
        :return:
        """
        # Check if it's on the right state
        if self.parse_state():
            return True
        return False

    @timeit
    def parse_attempt(self, attempt):
        """
        Check if the service_attempt should be passive of a handler call
        :return: bool
        """

        try:
            if int(self.service_attempt) >= int(attempt):
                return True
            else:
                return False
        except:
            print "Service attempt is not a number!"
            exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
