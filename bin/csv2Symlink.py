#!/usr/bin/env python

import csv, os, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('csv_file_path')
parser.add_argument('root_column')
parser.add_argument('relpath_column')
parser.add_argument('dest_path')

if __name__ == '__main__':
    args = parser.parse_args()
    result_dict_list = []
    csv_file_path = args.csv_file_path
    # csv_file_path = '/home/oezdemir/PycharmProjects/ome_zarr_tools/acsv_example/datasets.txt'
    # dircol = 'PathName_Result.Image_IMG'
    dircol = args.root_column
    # namecol = 'FileName_Result.Image_IMG'
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
        dirpath = os.path.dirname(os.path.abspath(csv_file_path))
        print(dirpath)
        dirname = dictitem[dircol].replace('root/', '')
        name = dictitem[namecol]
        fpath = os.path.join(dirpath, dirname, name)
        os.symlink(fpath, os.path.join(destdir, os.path.basename(name)))

