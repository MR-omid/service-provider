import builtins
import subprocess
from time import sleep


class File(object):
    """A basic file-like object."""

    def __init__(self, path, *args, **kwargs):
        self._file = builtins.open(path, *args, **kwargs)
        print('init')

    def read(self, n_bytes=-1):
        print('read')
        data = self._file.read(n_bytes)
        return data

    def fileno(self):
        print('fileno')
        return self._file.fileno()

    def write(self, s):
        print('write')
        self._file.write(s)

    def writelines(self, lines):
        print('writelines')
        self._file.writelines(lines)

    def __enter__(self):
        print('enter')
        return self

    def __exit__(self, e_type, e_val, e_tb):
        print('exit')
        self._file.close()
        self._file = None

    def __call__(self, *args, **kwargs):
        print('call')


def fop(path, *args, **kwargs):
    return File(path, *args, **kwargs)
with fop('fg.txt','w+') as ot:
    p = subprocess.Popen(['python3','aaa.py'],stdout=ot)
    sleep(100)