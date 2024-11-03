#!/usr/bin/env python

import csv, os, sys, argparse, glob, shutil
from pathlib import Path

from directory2symlink import makelinks


parser = argparse.ArgumentParser()
parser.add_argument('csv_file_path')
parser.add_argument('root_column')
parser.add_argument('relpath_column')
parser.add_argument('dest_path')
parser.add_argument('--contains', default = None)
parser.add_argument('--ignores', default = None)


if __name__ == '__main__':
    args = parser.parse_args()
    result_dict_list = []
    csv_file_path = args.csv_file_path

    dircol = args.root_column
    namecol = args.relpath_column
    destdir = args.dest_path

    os.makedirs(destdir, exist_ok = True)

    result_dict_list = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            result_dict_list.append(row)

    pathlist = []
    for dictitem in result_dict_list:
        if dircol in dictitem:
            root = dictitem[dircol].replace('root/', '')
        elif dircol in ("auto", None, ""):
            root = os.path.dirname(csv_file_path)
        else:
            raise Exception(f"The specified root column '{dircol}' does not exist.")

        if namecol in dictitem:
            relpath = dictitem[namecol]
        else:
            raise Exception(f"The specified name column '{namecol}' does not exist.")

        if relpath.startswith('/'):
            assert dircol in ("auto", None, ""), f"A relative path cannot start with a '/'."
            # relpath = relpath[1:]
            fpath = relpath
        else:
            fpath = os.path.join(root, relpath)
        pathlist.append(fpath)

    makelinks(pathlist, destdir,
              replace_outpath = False,
              contains = args.contains,
              ignores = args.ignores)

