#!/usr/bin/python
# -*- coding: utf-8 -*-
# author: Jan Hybs


import argparse
import threading
from datetime import datetime, timedelta
import time
import psutil
import sys
import signal


def create_parser():
    parser = argparse.ArgumentParser("exec_with_limit")
    parser.add_argument('--limit-time', '-t', dest='time_limit', type=parse_float, help=
"""Wall clock time limit for execution in seconds or in HH:MM:SS format
For precision use float value
""")
    parser.add_argument('--limit-memory', '-m', dest='memory_limit', type=float, help=
"""Memory limit per node in MB
For precision use float value
""")
    parser.add_argument('args', nargs='*')
    return parser


def parse_float(value):
    """
    Simple method for converting duration value
    Supported format are either number value or HH:MM:SS format

    :type value: str
    :rtype: float
    """
    value = str(value)
    try:
        return float(value)
    except ValueError:
        time = datetime.strptime(value, "%H:%M:%S")
        delta = timedelta(hours=time.hour, minutes=time.minute, seconds=time.second)
        return delta.total_seconds()


class LimitMonitor(threading.Thread):
    """
    Class LimitMonitor monitors resources of PyPy process and terminates
    PyPy if limits are not withheld.
    :type process: scripts.psutils.Process
    """

    CAUSE_TIME_LIMIT = 1
    CAUSE_MEMORY_LIMIT = 2

    def __init__(self, pypy):
        super(LimitMonitor, self).__init__()
        self.process = pypy
        self.memory_limit = None
        self.time_limit = None

        self.terminated = False
        self.terminated_cause = 0

        self.memory_usage = 0
        self.memory_used = 0
        self.start_time = 0
        self.runtime = 0
        self.running = True

    def set_limits(self, time_limit=None, memory_limit=None):
        """
        :type time_limit: float
        :type memory_limit: float
        """
        self.time_limit = time_limit
        self.memory_limit = memory_limit

    def run(self):
        self.start_time = time.time()
        while self.running:
            self.update()
            time.sleep(.5)

    def update(self):
        if self.terminated:
            return

        if self.time_limit:
            try:
                self.runtime = self.process.runtime()
                if self.runtime > self.time_limit:
                    sys.stderr.write('Time limit exceeded! {:1.2f}s of runtime, {:1.2f}s allowed\n'.format(
                        self.runtime, self.time_limit
                    ))
                    self.terminated_cause = self.CAUSE_TIME_LIMIT
                    self.terminated = True
                    ProcessUtils.secure_kill(self.process)
                    return
            except AttributeError as e2:
                pass

        if self.memory_limit:
            try:

                self.memory_usage = self.process.memory_usage()
                self.memory_used = max(self.memory_used, self.memory_usage)
                if self.memory_usage > self.memory_limit:
                    sys.stderr.write('Memory limit exceeded! {:1.2f}MB used, {:1.2f}MB allowed\n'.format(
                        self.memory_usage, self.memory_limit
                    ))
                    self.terminated_cause = self.CAUSE_MEMORY_LIMIT
                    self.terminated = True
                    ProcessUtils.secure_kill(self.process)
                    return
            except AttributeError as e2:
                pass


class ProcessUtils(object):
    """
    Class ProcessUtils is utils class dealing with processes
    """

    KB = 1000.0
    MB = KB ** 2
    GB = KB ** 3

    KiB = 1024.0
    MiB = KiB ** 2
    GiB = KiB ** 3

    _reasonable_amount_of_time = 1
    _just_a_sec = 0.1

    @classmethod
    def list_children(cls, process):
        """
        :type process: psutil.Process
        """
        result = []
        for child in process.children():
            if process.pid == child.pid:
                continue
            result.extend(cls.list_children(child))
        result.append(process)
        return result

    @classmethod
    def get_memory_info(cls, process, prop='vms', units=MiB):
        """
        :type process: psutil.Process
        """
        children = cls.list_children(process)
        total = 0
        for child in children:
            try:
                total += getattr(child.memory_info(), prop)
            except psutil.NoSuchProcess:
                continue
        return total / units

    @classmethod
    def apply(cls, children, prop, *args, **kwargs):
        result = []
        for child in children:
            try:
                result.append(getattr(child, prop)(*args, **kwargs))
            except psutil.NoSuchProcess as e: pass
        return result

    @classmethod
    def terminate(cls, process):
        cls.terminate_all(cls.list_children(process))

    @classmethod
    def terminate_all(cls, children):
        cls.apply(children, 'terminate')

    @classmethod
    def kill(cls, process):
        cls.kill_all(cls.list_children(process))

    @classmethod
    def kill_all(cls, children):
        cls.apply(children, 'kill')

    @classmethod
    def secure_kill(cls, process):
        # first, lets be reasonable and terminate all processes (SIGTERM)
        children = cls.list_children(process)
        cls.terminate_all(children)

        # wait jus a sec to let it all blend in
        time.sleep(cls._just_a_sec)

        # if some process are still running
        if True in cls.apply(children, 'is_running'):
            # wait a bit to they can safely exit...
            time.sleep(cls._reasonable_amount_of_time)
            # check status again, maybe perhaps they finish what
            # they have started and are done?
            if True in cls.apply(children, 'is_running'):
                # looks like they are still running to SIGKILL 'em
                cls.kill_all(children)
            else:
                # all processes finish they job in reasonable period since
                # SIGTERM was sent
                return True
        else:
            # all processes finish right after* SIGTERM was announced
            return True

        # return max value either True or False
        # False meaning some process is still running

        return not max(cls.apply(children, 'is_running'))


class try_catch(object):
    """
    Decorator which uses cache for certain amount of time
    """

    def __init__(self, default=0):
        self.default = default

    def __call__(self, f):
        # call wrapped function or use caches value
        def wrapper(other, *args, **kwargs):
            try:
                return f(other, *args, **kwargs)
            except psutil.NoSuchProcess:
                return self.default

        return wrapper

KB = 1000.0
MB = KB ** 2
GB = KB ** 3

KiB = 1024.0
MiB = KiB ** 2
GiB = KiB ** 3

# duration used in process kill
_reasonable_amount_of_time = 1
_just_a_sec = 0.1


class Process(psutil.Process):
    """
    Implementation of Process under linux
    """

    platform = 'windows'

    @classmethod
    def popen(cls, *args, **kwargs):
        process = psutil.Popen(*args, **kwargs)
        return Process(process.pid, process)

    # @classmethod
    # def _popen(cls, *args, **kwargs):
    #     process = psutil.Popen(*args, **kwargs)
    #     return Process(process.pid)

    def __init__(self, pid, process=None):
        """
        :type process: psutil.Popen
        """
        super(Process, self).__init__(pid)
        self.process = process
        self.terminated = False

    def wait(self, timeout=None):
        if self.process:
            return self.process.wait()
        return super(Process, self).wait(timeout)

    @property
    def returncode(self):
        if self.terminated:
            return 1
        if self.process:
            return self.process.returncode

    def children(self, recursive=True):
        children = super(Process, self).children(recursive)
        children = [Process(x.pid) for x in children]
        children.append(self)
        return children

    @try_catch(default=0)
    def memory_usage(self, prop='rss', units=MiB):
        # use faster super call
        children = super(Process, self).children(True)
        children.append(self)

        # put usages to list
        usages = self.apply(children, 'memory_info')
        if not usages:
            return 0.0
        return sum([getattr(x, prop) for x in usages]) / units

    @try_catch(default=0)
    def runtime(self):
        return time.time() - self.create_time()

    @try_catch(default=True)
    def secure_kill(self):
        # first, lets be reasonable and terminate all processes (SIGTERM)
        self.terminated = True
        children = self.children()
        self.apply(children, 'terminate')

        # wait jus a sec to let it all blend in
        time.sleep(_just_a_sec)

        # if some process are still running
        if True in self.apply(children, 'is_running'):
            # wait a bit to they can safely exit...
            time.sleep(_reasonable_amount_of_time)
            # check status again, maybe perhaps they finish what
            # they have started and are done?
            if True in self.apply(children, 'is_running'):
                # looks like they are still running to SIGKILL 'em
                self.apply(children, 'kill')
            else:
                # all processes finish they job in reasonable period since
                # SIGTERM was sent
                return True
        else:
            # all processes finish right after* SIGTERM was announced
            return True

        # return max value either True or False
        # False meaning some process is still running

        return not max(self.apply(children, 'is_running'))

    @classmethod
    def apply(cls, children, prop, *args, **kwargs):
        result = []
        for child in children:
            try:
                result.append(getattr(child, prop)(*args, **kwargs))
            except psutil.NoSuchProcess as e:
                pass
        return result


def signal_handler(signal, frame):
    """
    When ctrl + c is caught (SIGINT) will terminate monitor
    and exit with code 127
    :param signal:
    :param frame:
    :return:
    """
    sys.stderr.write('KeyboardInterrupt \n')
    try:
        monitor.running = False
    except: pass
    sys.exit(127)


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if not args.args:
        parser.print_usage()
        sys.exit(1)

    try:
        process = Process.popen(args.args)
    except FileNotFoundError:
        sys.stderr.write('%s: command not found\n' % args.args[0])
        sys.exit(127)

    signal.signal(signal.SIGINT, signal_handler)
    # create monitor
    monitor = LimitMonitor(process)
    monitor.set_limits(args.time_limit, args.memory_limit)
    monitor.start()

    # wait for process to end
    process.wait()
    monitor.running = False
    monitor.join()

    # exit with process exit code
    sys.exit(monitor.process.returncode)
