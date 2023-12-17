#!/usr/bin/env python
import subprocess
import argparse
import json
import os
import sys

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__)) # /home/oezdemir/PycharmProjects/nfprojects/bftools/modules/templates
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

    # os.chdir(scriptpath) #
    # os.chdir('..') # /home/oezdemir/PycharmProjects/nfprojects ### note that this is the execution directory.
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    with open(paramfile, 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = parser.parse_args(namespace = t_args)
        # print(args)
    # keys = args.__dict__.keys()
    logdir = os.path.join(args.workdir, 'logs/.nextflow.log')

    cmd0 = []
    cmd0 += ["nextflow", "-C", configfile, "-log", logdir]
    if args.output_type == 'ometiff':
        cmd0 += ["run", f"{scriptpath}/../pff2ometiff.nf"]
    elif args.output_type == 'omezarr':
        cmd0 += ["run", f"{scriptpath}/../pff2omezarr.nf"]
    cmd0 += [f"-params-file", paramfile, "-profile", args.profile]
    cmd1 = ["nextflow", "clean", "but", "none", "-n", "-f"]
    # print(cmd0)
    # print(cmd1)
    # cmd += ["cd - && \\\n"]
    subprocess.run(cmd0, check = True, shell = False)
    subprocess.run(cmd1, check = True, shell = False)




