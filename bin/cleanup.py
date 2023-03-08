#!/usr/bin/env python
import os, shutil, glob
import json




if __name__ == "__main__":
    relpath = os.getcwd()
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(scriptpath, '..', 'params', 'params.json'), 'r+') as f:
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
            print(pattern_files)
            for item in pattern_files:
                os.remove(item)
        except:
            pass
