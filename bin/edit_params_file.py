#!/usr/bin/env python
import argparse
import json
import os, shutil

### This is also a good demonstration of json and argparse compatibility.

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__)) # /home/oezdemir/PycharmProjects/nfprojects/bftools/modules/templates
    os.chdir(scriptpath)
    # params_path = '../params/pff2ometiff_params.json'
    # defparams_path = '../params/pff2ometiff_params.json.default'
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f')
    parser.add_argument('--default_file', '-df')
    parser.add_argument('--key', default = 'newparam')
    parser.add_argument('--deletekey', default = 'false')
    parser.add_argument('--value', default = 3)
    args = parser.parse_args()
    if not os.path.exists(args.file):
        shutil.copy(args.default_file, args.file)
    with open(args.file, 'r+') as f:
        jsonfile = json.load(f)
        if args.deletekey == 'true':
            if args.key in jsonfile.keys():
                del jsonfile[args.key]
        else:
            jsonfile[args.key] = args.value
        f.seek(0)
        json.dump(jsonfile, f, indent = 2)
        f.truncate()