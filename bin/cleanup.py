#!/usr/bin/env python
import os, shutil, glob
import json



if __name__ == "__main__":
    homepath = os.environ.get('HOMEPATH')
    temppath = os.environ.get('TEMPPATH')
    parampath = os.environ.get('PARAMPATH')
    defparamfile = os.path.join(parampath, 'params.json.default')
    backupparamfile = os.path.join(parampath, 'params.json.backup')
    paramfile = os.path.join(parampath, 'params.json')

    relpath = os.getcwd()
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    with open(paramfile, 'r+') as f:
        jsonfile = json.load(f)
        # keep_workdir = jsonfile['keep_workdir']
        inpath = jsonfile['in_path']
        removal = os.path.join(inpath, 'tempdir')
        try:
            shutil.rmtree(removal)
        except:
            pass
        try:
            removal = os.path.join(inpath, '*pattern')
            pattern_files = glob.glob(removal)
            # print(pattern_files)
            for item in pattern_files:
                os.remove(item)
        except:
            pass
