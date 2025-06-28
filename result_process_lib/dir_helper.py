from os import listdir
from os.path import isdir, join


def get_dirs(path):
    return [f for f in listdir(path) if isdir(join(path, f)) and not f.startswith('.')]
