#!/usr/bin/env python
import subprocess
import argparse
import os, sys, argparse, glob, shutil, json
from pathlib import Path

# def makelinks(inpath,
#               outpath,
#               contains = None,
#               ignores = None
#               ):
#     if isinstance(inpath, Path):
#         inpath = inpath.as_posix()
#     if isinstance(outpath, Path):
#         outpath = outpath.as_posix()
#     if '**' in inpath:
#         paths = glob.glob(inpath, recursive = True)
#     elif '*' in inpath:
#         paths = glob.glob(inpath)
#     else:
#         paths = glob.glob(os.path.join(inpath, '*'))
#
#     if os.path.exists(outpath):
#         shutil.rmtree(outpath)
#     os.makedirs(outpath)
#
#     for path in paths:
#         if os.path.isfile(path):
#             if contains is None and ignores is None:
#                 os.symlink(path, os.path.join(outpath, os.path.basename(path)))
#             elif ignores is not None:
#                 if ignores not in path:
#                     os.symlink(path, os.path.join(outpath, os.path.basename(path)))
#             elif contains is not None:
#                 if contains in path:
#                     os.symlink(path, os.path.join(outpath, os.path.basename(path)))
#
#     return outpath

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    homepath = os.environ.get('HOMEPATH')
    temppath = os.environ.get('TEMPPATH')
    parampath = os.environ.get('PARAMPATH')
    configpath = os.environ.get('CONFIGPATH')
    defparamfile = os.path.join(parampath, 'params.json.default')
    backupparamfile = os.path.join(parampath, 'params.json.backup')
    paramfile = os.path.join(parampath, 'params.json')
    configfile = os.path.join(configpath, 'bftools.config')

    if not os.path.exists(parampath):
        os.makedirs(parampath)
    if not os.path.exists(configpath):
        os.makedirs(configpath)
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if not os.path.exists(homepath):
        os.makedirs(homepath)

    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    with open(paramfile, 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = parser.parse_args(namespace = t_args)

    logdir = os.path.join(args.workdir, 'logs/.nextflow.log')

    cmd0 = []
    cmd0 += ["nextflow", "-C", configfile, "-log", logdir]
    if args.output_type == 'ometiff':
        cmd0 += ["run", f"{scriptpath}/../pff2ometiff.nf"]
    elif args.output_type == 'omezarr':
        cmd0 += ["run", f"{scriptpath}/../pff2omezarr.nf"]
    cmd0 += [f"-params-file", paramfile, "-profile", args.profile]
    cmd1 = ["nextflow", "clean", "but", "none", "-n", "-f"]

    curpath = os.getcwd()
    os.chdir(temppath)
    subprocess.run(cmd0, check = True, shell = False)
    subprocess.run(cmd1, check = True, shell = False)
    os.chdir(curpath)




