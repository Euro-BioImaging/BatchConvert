#!/usr/bin/env python
import os, re
import shutil
import copy
from collections import Counter


transpose_list = lambda l: list(map(list, zip(*l)))

def __verify_regular_increments(flatlist):
    # flatlist = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
    diff = flatlist[1] - flatlist[0]
    for i in range(1, len(flatlist)):
        item0 = flatlist[i - 1]
        item1 = flatlist[i]
        if (item1 - item0) != diff:
            print("The increment within one of the numeric fields is not unique. Verification fails.")
            return False
        else:
            diff = item1 - item0
    return True


def __find_uniques(flatlist):
    count_dict = Counter(flatlist)
    uqs = list(dict.fromkeys(count_dict))
    return uqs, count_dict

def __verify_incrementation(flatlist):
    # flatlist = field
    uqs, count_dict = __find_uniques(flatlist)
    if len(uqs) <= 1:
        print("A numeric field with single unique value detected.")
        return True
    regularity = __verify_regular_increments(uqs)
    counts = transpose_list(count_dict.items())[1]
    count_uniqueness, _ = __find_uniques(counts)
    if regularity:
        if len(count_uniqueness) > 1:
            print("Increment groups have variable sizes. The size should be unique. Verification fails.")
            return False
        else:
            return True
    else:
        return False

def isin_same_group(file0, file1):
    """
    To be grouped together, there are certain criteria:
    1. The two filenames must have the same length.
    2. The non-numerical part of the filenames must exactly match
    3. If there are multiple non-numerical fields, their numbers must match for both filenames
    """
    if not len(file0) == len(file1):
        return False
    numerical0 = [item for item in file0 if item.isnumeric()]
    numerical1 = [item for item in file1 if item.isnumeric()]
    newfile0 = file0
    newfile1 = file1
    for item in numerical0:
        newfile0 = newfile0.replace(str(item), '')
    for item in numerical1:
        newfile1 = newfile1.replace(str(item), '')
    if newfile0 != newfile1:
        return False
    numerical0 = list(map(int, re.findall(r'\d+', file0)))
    numerical1 = list(map(int, re.findall(r'\d+', file1)))
    if len(numerical0) == len(numerical1):
        return True
    else:
        return False

def group_filelist(filelist):
    groups = []
    group = []
    for i in range(1, len(filelist)):
        file0 = filelist[i-1]
        file1 = filelist[i]
        if isin_same_group(file0, file1):
            group.append(file0)
            if i == (len(filelist) - 1):
                group.append(file1)
        else:
            group.append(file0)
            groups.append(group)
            group = []
            if i == (len(filelist) - 1):
                group.append(file1)
    groups.append(group)
    if len(groups) == 0:
        if len(group) > 0:
            groups.append(group)
    return groups


def proofread_group(filegroup):
    # filegroup = groups[1]
    numeric_fields = []
    for file in filegroup:
        numerical = list(map(int, re.findall(r'\d+', file)))
        if not len(numerical):
            print("At least one of the group files contains no numeric field.")
            return False
        numeric_fields.append(numerical)
    numeric_fields = transpose_list(numeric_fields)
    for i, field in enumerate(numeric_fields):
        is_verified = __verify_incrementation(field)
        if is_verified:
            pass
        else:
            print("At least one of the numeric fields fails to follow a regular incrementation pattern.")
            print("Check the numeric field corresponding to index %s" % i)
            return False
    return True


def proofread_group_patterns(filelist):
    # filelist = os.listdir(rootDir)
    filelist.sort()
    groups = group_filelist(filelist)
    proofread = {}
    failed_groups = {}
    print("%s groups detected" % len(groups))
    print("####################################################################################")
    for i, gr in enumerate(groups):
        print("Group no %s is being investigated" % i)
        is_proofread = proofread_group(gr)
        if is_proofread:
            proofread[i] = gr
            print("Group no %s passes proofreading." % i)
            print("####################################################################################")
        elif not is_proofread:
            failed_groups[i] = gr
            print("Group no %s fails proofreading and will be excluded from the pattern file creation." % i)
            print("####################################################################################")
    return proofread, failed_groups

# flatlist = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 7, 7, 7]
# __verify_incrementation(flatlist)

def save_pattern_file(rootDir, filelist, concatenation_axes = 'auto'):
    assert isinstance(concatenation_axes, type('')), 'concatenation_axes must be in type str.'
    assert isinstance(rootDir, type('')), 'rootDir must be in type str.'
    last = filelist[-1]
    zonelists = []
    zonelist_ids = []
    for file in filelist:
        # zonelist = list(map(int, re.findall(r'\d+', file)))
        # zoneids = [(m.start(0), m.end(0)) for m in re.finditer(r'\d+', file)]
        zonelist, zonelistidx = [], []
        for m in re.finditer(r'\d+', file):
            zoneidx = (m.start(0), m.end(0))
            zone = file[zoneidx[0]:zoneidx[1]]
            zonelistidx.append(zoneidx)
            zonelist.append(zone)
        zonelist_ids.append(zonelistidx)
        zonelists.append(zonelist)
    zonelistlen = len(zonelist)
    zonelistdict = {}
    zonelist_ids_dict = {}
    for i in range(zonelistlen):
        zonelistdict[i] = []
        zonelist_ids_dict[i] = []
    for zonelist, zonelistidx in zip(zonelists, zonelist_ids): ### TODO Change this to a (faster) transpose_dict function
        for i in range(zonelistlen):
            zonelistdict[i].append(zonelist[i])
            zonelist_ids_dict[i].append(zonelistidx[i])
    variable_zones = []
    patterns = []
    variable_zone_ids = []
    reg = last
    for i in range(zonelistlen):
        dictitem = zonelistdict[i]
        dictitem.sort()
        minval = dictitem[0]
        maxval = dictitem[-1]
        zonelist_ids = zonelist_ids_dict[i]
        if (len(filelist) > 1) and (minval == maxval):
            pass
        else:
            variable_zones.append((minval, maxval))
            pattern = '<%s-%s>' % (minval, maxval)
            variable_zone_ids.append(zonelist_ids[-1])
            patterns.append(pattern)

    ### Make sure that the user inserted the fitting number of concatenation axes
    if concatenation_axes != 'auto':
        assert len(concatenation_axes) == len(patterns), "The specified number of axes does not match the number of detected variable zones, which is %s." % len(patterns)

    ### Modify the pattern files to make sure the user-specified axes are inserted
        for i in range(len(patterns)):
            patterns[i] = '%s' % concatenation_axes[i].capitalize() + patterns[i]

    ### Create the regex according to the detected variable zones
    oldreg = reg
    diff = 0
    for pattern, variable_zone_idx in zip(patterns, variable_zone_ids):
        idx0, idx1 = variable_zone_idx
        idx0 += diff; idx1 += diff
        reg = reg[:idx0] + pattern + reg[idx1:]
        diff = len(reg) - len(oldreg)
        oldreg = reg

    #################################################################################################################################
    ################ So the pattern file is thus generated. Now, the real file names must be modified if needed #####################
    #################################################################################################################################

    if concatenation_axes == 'auto':
        newDir = rootDir
    else:
        newfilelist = copy.deepcopy(filelist)
        for i, file in enumerate(newfilelist):
            oldfile = file
            diff = 0
            for j, variable_zone_idx in enumerate(variable_zone_ids):
                idx0, idx1 = variable_zone_idx
                idx0 += diff
                idx1 += diff
                listing = list(file)
                listing.insert(idx0, concatenation_axes[j].capitalize())
                file = ''.join(listing)
                diff = len(file) - len(oldfile)
                oldfile = file
            newfilelist[i] = file
        assert len(newfilelist) == len(filelist), 'newfilelist and filelist do not have the same length.'

        newDir = rootDir + '/tempdir'

        try:
            os.makedirs(newDir)
        except:
            pass

        for olditem, newitem in zip(filelist, newfilelist):
            oldpath = os.path.join(rootDir, olditem)
            newpath = os.path.join(newDir, newitem)
            shutil.copy(oldpath, newpath)
    return reg, newDir

def save_pattern_file_per_group(rootDir, concatenation_axes = ['auto'], select_by = ''):
    assert isinstance(rootDir, type('')), 'rootDir must be in type str.'
    assert isinstance(select_by, type('')), 'select_by must be in type str.'
    filelist_unfiltered = os.listdir(rootDir)
    filelist = list(filter(lambda iterable: select_by in iterable, filelist_unfiltered))
    proofread, failed_groups = proofread_group_patterns(filelist)
    regs = []

    gr_num = len(proofread.keys())
    if (len(concatenation_axes) == 1) & (concatenation_axes[0] == 'auto'):
            axes_set = concatenation_axes * gr_num
    else:
        axes_set = concatenation_axes

    # print(proofread.items())
    # print(axes_set)
    for i, (idx, gr) in enumerate(proofread.items()):
        axes = axes_set[i]
        reg, newDir = save_pattern_file(rootDir, gr, axes)
        with open(newDir + '/gr%s.pattern' % idx, 'w') as writer:
            writer.write(reg)
        regs.append(reg)
    return regs
