import ctypes
import shlex
import subprocess

import win32con
import win32event
import win32process
from win32com.shell import shellcon
from win32com.shell.shell import ShellExecuteEx


def is_administrator():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        # probably no administrator rights
        return False


def run_as_administrator(cmd: list):
    if not is_administrator():
        cmd_exec = cmd[0]
        params = shlex.join(cmd[1:])

        info = ShellExecuteEx(
            fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
            lpVerb='runas',
            lpFile=cmd_exec,
            lpParameters=params,
            nShow=win32con.SW_SHOWNORMAL,
        )

        handle = info['hProcess']
        win32event.WaitForSingleObject(
            handle,
            win32event.INFINITE,
        )
        rc = win32process.GetExitCodeProcess(handle)
        assert rc == 0
    else:
        subprocess.run(cmd)
