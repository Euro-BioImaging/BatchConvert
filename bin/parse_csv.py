#!/usr/bin/env python

import copy, csv, os, sys, argparse

def validate_path(ref_dir, pth): # ref_dir is where the csv file is located.
    if pth is None or pth == '':
        pth = ''
    if pth.startswith('/'):
        pass
    else:  # pth is given as a relative path. Verify it.
        jnpth = os.path.join(ref_dir, pth)
        if os.path.exists(jnpth):
            pth = os.path.abspath(jnpth)
        else:
            if pth.startswith('root/'):
                pth = pth.replace('root/', '')
            elif pth.startswith('root'):
                pth = pth.replace('root', '')
            jnpth = os.path.join(ref_dir, pth)
            if os.path.exists(jnpth):
                pth = os.path.abspath(jnpth)
            else:
                raise ValueError(f"The path {jnpth} is not valid.")
    return pth

def robust_parse_csv(csv_sourcepath: str = "/home/oezdemir/PycharmProjects/nextflow_convert/test_csv/testimages.csv",
                     csv_destpath: str = "/home/oezdemir/PycharmProjects/nextflow_convert/test_csv/testimages_parsed.csv",
                     colname_parent: str = "RootPath",
                     colname_relative: str = "RelativePath_Result.Image_IMG",
                     pattern: str = None,
                     rpattern: str = None,
                     endpoint: str = "local"
                     ):

    fieldnames = None

    dictlist = []
    with open(csv_sourcepath, 'r') as csv_file:
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        csv_reader = csv.DictReader(csv_file, dialect=dialect)
        for row in csv_reader:
            dictlist.append(row)

    # dictlist = []
    # with open(csv_sourcepath, 'r') as csv_file:
    #     csv_reader = csv.DictReader(csv_file)
    #     for row in csv_reader:
    #         dictlist.append(row)

    newlist = []
    for dictitem in dictlist:
        if fieldnames is None:
            fieldnames = list(dictitem.keys())
        else:
            assert fieldnames == list(dictitem.keys())

        # print(f"parent: {colname_parent}")
        if colname_parent == '' or colname_parent =="null" or colname_parent is None:
            rootpath = ''
        elif colname_parent in dictitem.keys():
            rootpath = dictitem[colname_parent]
        else:
            print(f"keys are: {list(dictitem.keys())}")
            raise ValueError(f"{colname_parent} could not be found in the column names.")

        if colname_relative == '' or colname_relative =="null" or colname_relative is None:
            raise ValueError(f"The relative paths cannot be an empty string or None. Individual files must be specified.")
        elif colname_relative in dictitem.keys():
            relpath = dictitem[colname_relative]
        else:
            raise ValueError(f"{colname_relative} could not be found in the column names.")

        if endpoint == "local":
            rootpath = validate_path(os.path.dirname(csv_sourcepath), rootpath)
        if relpath.startswith('/'): relpath = relpath[1:]
        fullpath = os.path.join(rootpath, relpath)

        newroot = os.path.dirname(fullpath)
        filename = os.path.basename(fullpath)

        fnameok = True
        if pattern is not None:
            if pattern not in filename:
                fnameok = False
        if rpattern is not None:
            if rpattern in filename:
                fnameok = False
        if fnameok:
            if colname_parent not in {None, 'None', "null", ''}:
                dictitem.pop(colname_parent)
            dictitem.pop(colname_relative)
            dictitem.update({f"RootOriginal": newroot, f"ImageNameOriginal": filename})
            newlist.append(dictitem)

    new_fieldnames = list(newlist[0].keys())
    os.makedirs(os.path.dirname(f'./{csv_destpath}'), exist_ok = True)

    # print(f"newlist: {newlist}")
    # print(f"new_fieldnames: {new_fieldnames}")

    with open(csv_destpath, 'w', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames = new_fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(newlist)

    return newlist

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_source_path')
    parser.add_argument('csv_dest_path')
    parser.add_argument('colname_parent')
    parser.add_argument('colname_relative')
    parser.add_argument('--pattern', '-p', default=None)
    parser.add_argument('--reject_pattern', '-rp', default=None)
    parser.add_argument('--endpoint', default = "local")
    args = parser.parse_args()
    filelist = robust_parse_csv(args.csv_source_path,
                                args.csv_dest_path,
                                args.colname_parent,
                                args.colname_relative,
                                args.pattern,
                                args.reject_pattern,
                                args.endpoint
                                )