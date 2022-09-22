import os
import sys


def main():
    cmd = [sys.executable, *sys.argv[1:]]

    if os.name == 'nt':
        from pysuperuser import windows
        windows.run_as_administrator(cmd)
    else:
        from pysuperuser import unix
        unix.run_as_root(cmd)


if __name__ == '__main__':
    main()
