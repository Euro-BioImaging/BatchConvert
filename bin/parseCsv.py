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
    # dircol = 'RootPath'
    dircol = args.root_column
    # namecol = 'RelativePath_Result.Image_IMG'
    namecol = args.relpath_column
    # destpath = '/home/oezdemir/PycharmProjects/ome_zarr_tools/acsv_example/datasets_parsed.txt'
    destpath = args.dest_path

    os.makedirs(os.path.dirname(f'./{destpath}'), exist_ok = True)

    dictlist = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dictlist.append(row)

    newlist = []
    for dictitem in dictlist:
        rootpath = dictitem[dircol]
        relpath = dictitem[namecol]
        filename = os.path.basename(relpath)
        pretext = os.path.dirname(relpath)
        newroot = os.path.join(rootpath, pretext)
        newitem = {dircol: newroot, namecol: filename}
        newlist.append(newitem)

    with open(destpath, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = [dircol, namecol])
        csv_writer.writeheader()
        csv_writer.writerows(newlist)



