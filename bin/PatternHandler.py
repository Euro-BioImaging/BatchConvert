#!/usr/bin/env python
import os, re
import shutil
import copy

def save_pattern_file(rootDir, concatenation_axes = 'infer_from_filenames'):
    assert isinstance(concatenation_axes, type('')), 'concatenation_axes must be in type str'
    assert isinstance(rootDir, type('')), 'rootDir must be in type str'
    filelist = os.listdir(rootDir)
    filelist.sort()
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
    for zonelist, zonelistidx in zip(zonelists, zonelist_ids):
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
        if minval == maxval:
            pass
        else:
            variable_zones.append((minval, maxval))
            pattern = '<%s-%s>' % (minval, maxval)
            variable_zone_ids.append(zonelist_ids[-1])
            patterns.append(pattern)

    ### Make sure that the user inserted the fitting number of concatenation axes
    if concatenation_axes != 'infer_from_filenames':
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

    if concatenation_axes == 'infer_from_filenames':
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
    with open(newDir + '/new.pattern', 'w') as writer:
        writer.write(reg)

    return reg