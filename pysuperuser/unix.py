import logging
import os
import shlex
import shutil
import subprocess

logger = logging.getLogger(__name__)


def run_as_root(cmd: list):
    if not os.geteuid() == 0:
        sudo_path = shutil.which('sudo')
        if sudo_path:
            cmd.insert(0, sudo_path)
        else:
            su_path = shutil.which('su')
            if su_path:
                sub_cmd = ' '.join(shlex.quote(arg) for arg in cmd)
                cmd = [
                    su_path,
                    '-c',
                    sub_cmd,
                ]
            else:
                logger.warning('no possibility found to run as root')

    subprocess.run(cmd)
