import ntpath
import os
import posixpath


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]


def ensure_posixpath(path):
    '''If the path given is not posix, convert it and return it, else return it'''
    splitted = path.split(ntpath.sep)
    if len(splitted) == 1:
        return path
    return posixpath.join(*splitted)


def ensure_ntpath(path):
    '''If the path given is not nt, convert it and return it, else return it'''
    splitted = path.split(posixpath.sep)
    if len(splitted) == 1:
        return path
    return ntpath.join(*splitted)


def ntpath_to_os_path(path):
    splitted = path.split(ntpath.sep)
    if len(splitted) == 1:
        return path
    return os.path.join(*splitted)
