#!/usr/bin/env python
import os, sys, argparse, glob, json, copy
import shutil
from pathlib import Path

def makelinks(inpath,
              outpath,
              contains = None,
              ignores = None,
              replace_outpath = True,
              files_only = 'False' # If true, do not symlink sub-directories.
              ):

    if isinstance(inpath, Path):
        inpath = inpath.as_posix()
    if isinstance(outpath, Path):
        outpath = outpath.as_posix()

    print(inpath)

    if isinstance(inpath, (list, tuple)):
        paths = inpath
    elif os.path.isfile(inpath):
        paths = glob.glob(inpath)
    else:
        if '**' in inpath:
            files_only = 'True' ## With the recursive option, do not symlink sub-directories.
            paths = glob.glob(inpath, recursive = True)
        elif '*' in inpath:
            paths = glob.glob(inpath)
            print(inpath, paths)
        else:
            paths = glob.glob(os.path.join(inpath, '*'))
    print(paths)

    if files_only in ('True', True):
        paths = [path for path in paths if os.path.isfile(path)]

    fpaths = copy.deepcopy(paths)
    print(fpaths)
    fpaths_s = [fpath.split('/') for fpath in fpaths]
    print(fpaths_s)
    for i, path in enumerate(fpaths_s):
        fpath = ['/' if item == '' else item for item in path]
        fpaths_s[i] = fpath
    print(fpaths_s)
    l = len(fpaths_s[0])
    shortest = fpaths_s[0]
    for fpath in fpaths_s:
        if len(fpath) < l:
            shortest = fpath
            l = len(fpath)
    for i in range(l):
        fields = [path[i] for path in fpaths_s]
        if all([field == shortest[i] for field in fields]):
            pass
        else:
            break

    basenames = ['_'.join(item[i:]) for item in fpaths_s]
    fnames = [item[-1] for item in fpaths_s]

    outfiles = []
    for i, basename in enumerate(basenames):
        names = copy.deepcopy(fnames)
        names.pop(i)
        fname = fnames[i]
        print(fname)
        if fname in names:
            outfiles.append(os.path.join(outpath, basename).replace(' ', '_'))
        else:
            outfiles.append(os.path.join(outpath, fname).replace(' ', '_'))
    ###
    filenames = [item[-1] for item in fpaths_s]

    if replace_outpath:
        if os.path.exists(outpath):
            shutil.rmtree(outpath)
    os.makedirs(outpath, exist_ok=True)

    symlink = lambda source, sink: os.symlink(source, sink) if not os.path.exists(sink) else None

    for path, name, outfile in zip(fpaths, filenames, outfiles):
        if contains in (None, 'None', '') and ignores in (None, 'None', ''):
            symlink(path, outfile)
        elif ignores not in (None, 'None', ''):
            if ignores not in name:
                symlink(path, outfile)
        elif contains not in (None, 'None', ''):
            if contains in name:
                symlink(path, outfile)
    return outpath



if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument('in_path')
    parser.add_argument('--contains', default=None)
    parser.add_argument('--ignores', default=None)
    parser.add_argument('--files_only', default = 'False', choices = ('True', 'False'))
    args = parser.parse_args()

    makelinks(args.in_path, 'symlinks', contains=args.contains, ignores=args.ignores, files_only=args.files_only)
