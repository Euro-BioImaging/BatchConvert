#!/usr/bin/env python
import subprocess
import argparse
import json
import os
import sys

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__)) # /home/oezdemir/PycharmProjects/nfprojects/bftools/modules/templates
    os.chdir(scriptpath) #
    os.chdir('..') # /home/oezdemir/PycharmProjects/nfprojects/bftools ### note that this is the execution directory.
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    # print("args are %s" % args)
    with open('./params/params.json', 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = parser.parse_args(namespace=t_args)
        # print(args)
    # keys = args.__dict__.keys()
    cmd = ["#!/usr/bin/env bash\n"]
    cmd += ["SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );\n"]
    cmd += ["nextflow -C $SCRIPTPATH/../configs/bftools.config -log $SCRIPTPATH/../WorkDir/logs/.nextflow.log"]
    if args.output_type == 'ometiff':
        cmd += [" run $SCRIPTPATH/../pff2ometiff.nf"]
    elif args.output_type == 'omezarr':
        cmd += [" run $SCRIPTPATH/../pff2omezarr.nf"]
    cmd += [" -params-file $SCRIPTPATH/../params/params.json"]
    cmd += [" -profile %s;\n" % args.profile]
    cmd += ["nextflow clean but none -n -f;"]
    # cmd += ["cd - && \\\n"]
    cmdstr = ''.join(cmd)
    sys.stdout.write(cmdstr)




