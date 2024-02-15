#!/usr/bin/env python

import csv, os, sys, argparse

parser = argparse.ArgumentParser()
parser.add_argument('csv_file_path')
parser.add_argument('root_column')
parser.add_argument('relpath_column')
parser.add_argument('dest_path')
parser.add_argument('--pattern', '-p', default = None)
parser.add_argument('--reject_pattern', '-rp', default = None)

if __name__ == '__main__':
    args = parser.parse_args()
    result_dict_list = []
    csv_file_path = args.csv_file_path
    dircol = args.root_column
    namecol = args.relpath_column
    destpath = args.dest_path
    pattern = args.pattern
    rpattern = args.reject_pattern

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
        if pretext.startswith('/'): pretext = pretext[1:]
        newroot = os.path.join(rootpath, pretext)

        fnameok = True
        if pattern is not None:
            if pattern not in filename:
                fnameok = False
        if rpattern is not None:
            if rpattern in filename:
                fnameok = False
        if fnameok:
            newitem = {f"RootOriginal": newroot, f"ImageNameOriginal": filename}
            newlist.append(newitem)

    with open(destpath, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = [f"RootOriginal", f"ImageNameOriginal"])
        csv_writer.writeheader()
        csv_writer.writerows(newlist)



# text = "MVI_<1349-1351:1>_Z<0>_C<00-06:2>.jpg"
# tlist = list(text)
# inds_lt = [i for i in range(len(tlist)) if tlist[i] == '<']
# inds_ht = [i for i in range(len(tlist)) if tlist[i] == '>']
# inds_dash = [i for i in range(len(tlist)) if tlist[i] == '-']
# inds_dots = [i for i in range(len(tlist)) if tlist[i] == ':']
# for idx in range(len(tlist)):
#     if idx in inds_lt:
#         tlist.pop(idx)
#         tlist.insert(idx, 's')
#     if idx in inds_ht:
#         tlist.pop(idx)
#         tlist.insert(idx, '')
#     if idx in inds_dots:
#         tlist.pop(idx)
#         tlist.insert(idx, 'step')
#     if idx in inds_dash:
#         for i,j in zip(inds_lt, inds_ht):
#             if (idx > i) and (idx < j):
#                 tlist.pop(idx)
#                 tlist.insert(idx, 'to')
# fname = ''.join(tlist)
# import os
# os.path.splitext(fname)[0] + '.pattern'
