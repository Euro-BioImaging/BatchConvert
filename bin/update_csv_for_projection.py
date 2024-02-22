#!/usr/bin/env python

# NOTE: THIS IS RESTRICTED TO INDEPENDENT CONVERSION AND CANNOT BE USED FOR GROUPED CONVERSION.
import copy
import csv, os, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('csv_file_path')
parser.add_argument('root_column')
parser.add_argument('relpath_column')
parser.add_argument('csv_dest_path')
parser.add_argument('csv_file_name')

if __name__ == '__main__':
    args = parser.parse_args()
    result_dict_list = []
    csv_file_path = args.csv_file_path

    dircol = args.root_column
    namecol = args.relpath_column

    destpath = args.csv_dest_path
    csvname = args.csv_file_name

    os.makedirs(os.path.dirname(f'./{destpath}'), exist_ok = True)

    dictlist = []
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            dictlist.append(row)

    newlist = []
    for dictitem in dictlist:
        newitem = copy.deepcopy(dictitem)

        rootpath = dictitem[dircol]
        relpath = dictitem[namecol]
        # import os
        # filename = "23052022_D3_0001.ome.zarr"
        filename = os.path.basename(relpath)
        filename_root = filename.split('.')[0]
        outext = '.'.join(filename.split('.')[1:])
        new_filename = filename_root + f"_apply_projection.{outext}"
        print(new_filename)
        pretext = os.path.dirname(relpath)
        newroot = os.path.join(rootpath, pretext)
        if newroot.endswith('/'):
            newroot = newroot[:-1]
        newitem.update({f"RootProjected": destpath, f"ImageNameProjected": new_filename})
        # newitem = {f"RootOriginal": newroot,
        #            f"ImageNameOriginal": filename,
        #            f"RootConverted": destpath,
        #            f"ImageNameConverted": new_filename}
        newlist.append(newitem)

    with open(csvname, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = list(newitem.keys()))
        csv_writer.writeheader()
        csv_writer.writerows(newlist)





