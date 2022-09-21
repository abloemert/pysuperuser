import multiprocessing
import shutil


def run_as_superuser(target):
    as_superuser_exec = shutil.which('python-as-superuser')
    if as_superuser_exec:
        ctx = multiprocessing.get_context('spawn')
        ctx.set_executable(as_superuser_exec)
        p = ctx.Process(target=target)
        p.start()
        p.join()
        assert p.exitcode == 0
    else:
        target()
