#!/usr/bin/env python

import os, json, subprocess

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    homepath = os.environ.get('HOMEPATH')
    temppath = os.environ.get('TEMPPATH')
    parampath = os.environ.get('PARAMPATH')
    defparamfile = os.path.join(parampath, 'params.json.default')
    backupparamfile = os.path.join(parampath, 'params.json.backup')
    paramfile = os.path.join(parampath, 'params.json')

    with open(paramfile, 'r+') as f:
        jsonfile = json.load(f)
        # keep_workdir = jsonfile['keep_workdir']
        if 'workdir' not in jsonfile.keys():
            pass
        else:
            workdir = jsonfile['workdir']
            paths = os.listdir(workdir)
            if len(paths) > 0:
                print("Cleaning work directory.")
            for fpath in paths:
                removal_path = os.path.join(workdir, fpath)
                cmd = ['rm', '-rf', removal_path]
                try:
                    subprocess.run(cmd)
                except:
                    pass

