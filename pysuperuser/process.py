import multiprocessing
import sys


class SuperuserProcess(multiprocessing.process.BaseProcess):
    _start_method = None

    @staticmethod
    def _Popen(process_obj):
        if sys.platform != 'win32':
            from pysuperuser.popen_posix import Popen
        else:
            from pysuperuser.popen_win32 import Popen
        return Popen(process_obj)

    @staticmethod
    def _after_fork():
        # process is spawned, nothing to do
        pass


def run_as_superuser(target):
    p = SuperuserProcess(target=target)
    p.start()
    p.join()
