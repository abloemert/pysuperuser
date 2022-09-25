import io
import logging
import os
import shlex
import shutil
from multiprocessing import popen_spawn_posix

logger = logging.getLogger(__name__)


class Popen(popen_spawn_posix.Popen):
    method = 'superuser'

    def _launch(self, process_obj):
        from multiprocessing import (
            resource_tracker,
            reduction,
            spawn,
            util,
            context,
        )
        tracker_fd = resource_tracker.getfd()
        self._fds.append(tracker_fd)
        prep_data = spawn.get_preparation_data(process_obj._name)
        fp = io.BytesIO()
        context.set_spawning_popen(self)
        try:
            reduction.dump(prep_data, fp)
            reduction.dump(process_obj, fp)
        finally:
            context.set_spawning_popen(None)

        parent_r = child_w = child_r = parent_w = None
        try:
            parent_r, child_w = os.pipe()
            child_r, parent_w = os.pipe()
            cmd = spawn.get_command_line(tracker_fd=tracker_fd,
                                         pipe_handle=child_r)
            exec_path = spawn.get_executable()
            if not os.geteuid() == 0:
                sudo_path = shutil.which('sudo')
                if sudo_path:
                    exec_path = sudo_path
                    cmd.insert(0, sudo_path)
                else:
                    su_path = shutil.which('su')
                    if su_path:
                        exec_path = su_path
                        sub_cmd = ' '.join(shlex.quote(arg) for arg in cmd)
                        cmd = [
                            su_path,
                            '-c',
                            sub_cmd,
                        ]
                    else:
                        logger.warning('no possibility found to run as root')

            self._fds.extend([child_r, child_w])
            self.pid = util.spawnv_passfds(exec_path,
                                           cmd, self._fds)
            self.sentinel = parent_r
            with open(parent_w, 'wb', closefd=False) as f:
                f.write(fp.getbuffer())
        finally:
            fds_to_close = []
            for fd in (parent_r, parent_w):
                if fd is not None:
                    fds_to_close.append(fd)
            self.finalizer = util.Finalize(self, util.close_fds, fds_to_close)

            for fd in (child_r, child_w):
                if fd is not None:
                    os.close(fd)
