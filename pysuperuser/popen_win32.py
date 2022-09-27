import _winapi
import ctypes
import msvcrt
import os
import signal
from multiprocessing import popen_spawn_win32

import win32con
import win32event
import win32process
from win32com.shell import shellcon
from win32com.shell.shell import ShellExecuteEx


class Popen(popen_spawn_win32.Popen):
    def __init__(self, process_obj):
        from multiprocessing import (
            reduction,
            spawn,
            util,
            context,
        )
        prep_data = spawn.get_preparation_data(process_obj._name)

        # read end of pipe will be duplicated by the child process
        # -- see spawn_main() in spawn.py.
        #
        # bpo-33929: Previously, the read end of pipe was "stolen" by the child
        # process, but it leaked a handle if the child process had been
        # terminated before it could steal the handle from the parent process.
        rhandle, whandle = _winapi.CreatePipe(None, 0)
        wfd = msvcrt.open_osfhandle(whandle, 0)
        cmd = spawn.get_command_line(parent_pid=os.getpid(),
                                     pipe_handle=rhandle)
        cmd = ' '.join('"%s"' % x for x in cmd)

        python_exe = spawn.get_executable()

        with open(wfd, 'wb', closefd=True) as to_child:
            # start process
            try:
                self.run_as_administrator(python_exe, cmd)
            except:
                _winapi.CloseHandle(rhandle)
                raise

            # set attributes of self
            self.returncode = None
            self.sentinel = int(self._handle)
            self.finalizer = util.Finalize(
                self,
                popen_spawn_win32._close_handles,
                (self.sentinel, int(rhandle)),
            )

            # send information to child
            context.set_spawning_popen(self)
            try:
                reduction.dump(prep_data, to_child)
                reduction.dump(process_obj, to_child)
            finally:
                context.set_spawning_popen(None)

    @staticmethod
    def is_administrator():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            # probably no administrator rights
            return False

    def run_as_administrator(self, python_exe: str, cmd: str):
        if not self.is_administrator():
            info = ShellExecuteEx(
                fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                lpVerb='runas',
                lpFile=python_exe,
                lpParameters=cmd,
                nShow=win32con.SW_SHOWNORMAL,
            )

            self._handle = info['hProcess']
        else:
            hp, ht, pid, tid = _winapi.CreateProcess(
                python_exe, cmd,
                None, None, False, 0, None, None, None)
            _winapi.CloseHandle(ht)
            self.pid = pid
            self._handle = hp

    def wait(self, timeout=None):
        if self.is_administrator():
            return super(Popen, self).wait(timeout)
        if self.returncode is None:
            if timeout is None:
                msecs = win32event.INFINITE
            else:
                msecs = max(0, int(timeout * 1000 + 0.5))

            res = win32event.WaitForSingleObject(
                self._handle,
                msecs,
            )
            if res == win32event.WAIT_OBJECT_0:
                code = win32process.GetExitCodeProcess(self._handle)
                if code == win32event.TERMINATE:
                    code = -signal.SIGTERM
                self.returncode = code

        return self.returncode
