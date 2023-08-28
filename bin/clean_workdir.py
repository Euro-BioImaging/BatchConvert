#!/usr/bin/env python

import os, json, subprocess

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(scriptpath, '..', 'params', 'params.json'), 'r+') as f:
        jsonfile = json.load(f)
        # keep_workdir = jsonfile['keep_workdir']
        workdir = jsonfile['workdir']
        paths = os.listdir(workdir)
        for fpath in paths:
            removal_path = os.path.join(workdir, fpath)
            cmd = ['rm', '-rf', removal_path]
            try:
                subprocess.run(cmd)
            except:
                pass

