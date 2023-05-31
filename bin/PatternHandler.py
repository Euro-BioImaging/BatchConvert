#!/usr/bin/env python
import os, re
import shutil
import copy
from collections import Counter
import itertools

transpose_list = lambda l: list(map(list, zip(*l)))
get_numerics = lambda string: list(re.findall(r'\d+', string))
get_alpha = lambda string: ''.join([i for i in string if not i.isnumeric()])

def flatten_list(l):
    return list(itertools.chain.from_iterable(l))

def get_elnum(listoflist):
    """
    Finds the number of elements in a list of list.
    This function assumes that the listoflist is two-dimensional.
    """
    flatlist = []
    for l in listoflist:
        flatlist += l
    return len(flatlist)

def find_uniques(flatlist):
    count_dict = Counter(flatlist)
    uqs = list(dict.fromkeys(count_dict))
    return uqs, count_dict

def get_size_grps(ilist):
    """ First process in filename regrouping. """
    grps = [[ilist[0]]]
    hold = len(ilist[0])
    for i in range(1, len(ilist)):
        if len(ilist[i]) == hold:
            grps[-1].append(ilist[i])
        else:
            grps.append([ilist[i]])
            hold = len(ilist[i])
    return grps

###############################################################################################################################
################################# Should the initial grouping be based on filename length ????? ###############################
###############################################################################################################################

# def get_size_grps(ilist):
#     # ilist = ['A1--W00001--P00001--Z00000--T00000--488nm.tif', 'A1--W00001--P00001--Z00000--T00000--561nm.tif', 'A1--W00001--P00001--Z00000--T00000--Transmission-CSU.tif', 'A1--W00001--P00002--Z00000--T00000--488nm.tif', 'A1--W00001--P00002--Z00000--T00000--561nm.tif', 'A1--W00001--P00002--Z00000--T00000--Transmission-CSU.tif', 'A2--W00002--P00001--Z00000--T00000--488nm.tif', 'A2--W00002--P00001--Z00000--T00000--561nm.tif', 'A2--W00002--P00001--Z00000--T00000--Transmission-CSU.tif', 'A2--W00002--P00002--Z00000--T00000--488nm.tif', 'A2--W00002--P00002--Z00000--T00000--561nm.tif', 'A2--W00002--P00002--Z00000--T00000--Transmission-CSU.tif']
#     """ First process in filename regrouping. """
#     ilist = sorted(ilist, key = len)
#     grps = [[ilist[0]]]
#     hold = len(ilist[0])
#     for i in range(1, len(ilist)):
#         if len(ilist[i]) == hold:
#             grps[-1].append(ilist[i])
#         else:
#             grps.append([ilist[i]])
#             hold = len(ilist[i])
#     return grps

def group_by_alpha(filelist):
    """ Second process in filename regrouping. """
    filelist.sort()
    alphas = []
    for item in filelist:
        alpha = get_alpha(item)
        alphas.append(alpha)
    uqs, count_dict = find_uniques(alphas)
    cts = [count_dict[key] for key in uqs]
    start = 0
    alphagrps = []
    for i in cts:
        alphagrps.append(filelist[start:start + i])
        start = start + i
    return alphagrps

def get_slices_from_list(ilist):
    start = 0
    slcs = []
    for i in range(0, len(ilist)):
        item = ilist[i]
        slc = slice(start, start + len(item))
        slcs.append(slc)
        start = start + len(item)
    return slcs

def group_preliminary(filelist):
    sizegrps = get_size_grps(filelist)
    fin = []
    for i, grp in enumerate(sizegrps):
        alphagrps = group_by_alpha(grp)
        fin += alphagrps
    return fin

def get_numeric_fields(group):
    ### This can only be applied to an alpha group
    nums = []
    for item in group:
        numerics = get_numerics(item)
        nums.append(numerics)
    numlists = transpose_list(nums)
    return numlists

def unify_identical_groups(slist):
    out = [slist[0]]
    for i in range(1, len(slist)):
        if slist[i] == slist[i - 1]:
            out[-1] += slist[i]
        else:
            out.append(slist[i])
    return out

def get_incremental_groups(slist, increment):
    grps = [[slist[0]]]
    for i in range(1, len(slist)):
        if int(slist[i]) - int(slist[i - 1]) == increment:
            grps[-1].append(slist[i])
        else:
            grps.append([])
            grps[-1].append(slist[i])
    return grps

def get_identity_groups(slist, get_slices = False):
    out = get_incremental_groups(slist, 0)
    if get_slices:
        out = get_slices_from_list(out)
    return out

def get_dynamic_incremental_groups(slist):
    # slist = [2, 2, 2, 4, 4, 4, 6, 6, 6, 2, 2, 2, 4, 4, 4, 6, 6, 6, 13, 1, 1, 1, 2, 2, 3, 3, 8, 8, 9, 9, 10, 10, 10, 11, 11, 11, 1, 2, 3, 4, 5]
    # slist = [2, 4, 6, 2, 4, 6, 1, 2, 3, 8, 9, 10]
    # slist = [0, 2, 4, 6, 0, 4]
    if len(slist) == 1:
        grps = [slist]
    else:
        grps = [[slist[0]]]
        increment = int(slist[1]) - int(slist[0])
        next = False
        for i in range(1, len(slist)):
            if int(slist[i]) - int(slist[i - 1]) == increment:
                grps[-1].append(slist[i])
                next = False
            else:
                grps.append([])
                if next:
                    increment = int(slist[i]) - int(slist[i - 1])
                grps[-1].append(slist[i])
                next = True
        ### Do the corrections
        grps_cp = copy.deepcopy(grps)
        i = 1; iters = len(grps)
        while i < iters:
            ### Correct the falsely separated unit groups that typically emerge from the process above
            if len(grps[i]) > 1:
                if int(grps[i][0]) - int(grps[i - 1][-1]) == int(grps[i][1]) - int(grps[i][0]):
                    grps[i] = grps[i - 1] + grps[i]
                    grps.pop(i - 1)
                    i = i - 1
                    iters -= 1
            i += 1
        ### Regroup if two groups are identical
        grps = unify_identical_groups(grps)
    return grps

def get_slices(nfield):
    # nfield = [2, 2, 2, 4, 4, 4, 6, 6, 6]
    # numfield1 = [2, 2, 2, 4, 4, 4, 6, 6, 6, 2, 2, 2]
    # nfield = [2, 2, 2, 4, 4, 4, 6, 6, 6, 2, 2, 2, 4, 4, 4, 6, 6, 6, 1, 1, 2, 2, 3, 3, 8, 8, 9, 9, 10, 10]
    # nfield = [0, 0, 0, 0, 1, 1]
    # nfield = [0, 0, 0, 0, 0, 0]
    # nfield = [None, None, None, None, None]
    uqs = Counter(nfield)
    if len(uqs) == 1:
        rslcs = [slice(0, len(nfield), None)]
    else:
        idgrps = get_incremental_groups(nfield, 0)
        idsizegrps = get_size_grps(idgrps)
        rslcs, jnslcflt = [], []
        sliceds = []
        for sizegrp in idsizegrps:
            uqs = [item[0] for item in sizegrp]
            dyngrps = get_dynamic_incremental_groups(uqs)
            # print(dyngrps)
            slcs = get_slices_from_list(dyngrps)
            sliced = [sizegrp[slc] for slc in slcs]
            sliceds.append(sliced)
            slcflt = [flatten_list(item) for item in sliced]
            jnslcflt += slcflt
        rslcs = get_slices_from_list(jnslcflt)
    return rslcs

def __get_numfield_intervals(grp):
    file = grp[-1]
    numfields, numfield_intervals = [], []
    for m in re.finditer(r'\d+', file):
        zoneidx = (m.start(0), m.end(0))
        zone = file[zoneidx[0]:zoneidx[1]]
        numfield_intervals.append(zoneidx)
        numfields.append(zone)
    return numfields, numfield_intervals

def _insert_dimension_specifiers(grp, concatenation_axes):
    numfields, nfintervals = __get_numfield_intervals(grp)
    newnames = copy.deepcopy(grp)
    if concatenation_axes is None:
        pass
    elif concatenation_axes == 'auto':
        pass
    else:
        for i, file in enumerate(grp):
            oldfile = file
            diff = 0
            for j, variable_zone_idx in enumerate(nfintervals):
                if concatenation_axes[j] == 'x':
                    pass
                elif concatenation_axes[j] == 'a':
                    pass
                else:
                    idx0, idx1 = variable_zone_idx
                    idx0 += diff
                    idx1 += diff
                    listing = list(file)
                    listing.insert(idx0, concatenation_axes[j].capitalize())
                    file = ''.join(listing)
                    diff = len(file) - len(oldfile)
                    oldfile = file
            newnames[i] = file
    return newnames

def check_if_auto(axes):
    # axes = ['aa', 'xaa', 'aa']
    if isinstance(axes, type('')):
        axes = [axes]
    if all([item == 'auto' for item in axes]):
        is_auto = True
    else:
        is_auto = True
        flattened = ''.join(tuple(axes))
        for i in flattened:
            if (i == 'x') | (i == 'a'):
                pass
            else:
                is_auto = False
    return is_auto

def parse_axes(axes, nfields):
    # axes = ['aa', 'xaa', 'xxxx']
    # axes = 'auto'
    # nfields = [[['23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022'], ['3', '3', '3', '3', '3', '3', '3', '3', '3', '3', '3', '3', '3', '3'], ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009', '0010', '0011', '0012', '0013', '0014']], [['23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022'], ['26', '26', '26', '26', '26', '26', '26', '26'], ['7', '7', '7', '7', '7', '7', '7', '7'], ['0000', '0001', '0002', '0003', '0004', '0005', '0006', '0007']], [['23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022', '23052022'], ['26', '26', '26', '26', '26', '26', '26', '26', '26', '26'], ['4', '4', '4', '4', '4', '4', '4', '4', '4', '4'], ['0000', '0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009']]]
    nfieldsize = [len(item) for item in nfields]
    newaxes = []
    if isinstance(axes, list):
        newaxes = copy.deepcopy(axes)
    else:
        newaxes = [axes]
    if len(newaxes) == 1:
        newaxes = newaxes * len(nfieldsize)
    print(newaxes)
    ####################################################################
    if len(newaxes) != len(nfieldsize):
        raise ValueError("Length of the axes list %s does not match the number of groups, which is %s." % (len(newaxes), len(nfieldsize)))
    final = []
    for axitem, size in zip(newaxes, nfieldsize):
        assert isinstance(axitem, str), "axis type must be string."
        if axitem == 'auto':
            axitem = 'a' * size
        if len(axitem) > size:
            raise ValueError("Axis number %s cannot be greater than the number of relevant numeric fields, which is %s" % (len(axitem), size))
        while len(axitem) != size: axitem = 'x' + axitem
        final.append(axitem)
    is_auto = check_if_auto(final)
    print(final, is_auto)
    return final, is_auto

class FilelistGrouper:
    def __init__(self, rootDir, concatenation_order = None, selby = None, rejby = None):
        # rootDir = "/home/oezdemir/PycharmProjects/nfprojects/daja"
        # selby, rejby = None, "Transmission"
        filelist = os.listdir(rootDir)
        self.rootDir = rootDir
        fl = copy.deepcopy(filelist)
        self.selby = selby
        self.rejby = rejby
        if selby is not None:
            fl = [item for item in fl if selby in item]
        if rejby is not None:
            fl = [item for item in fl if not rejby in item]
        self.fl = sorted(fl)
        self.fname_is_repaired = False
        self.__group_by_alpha()
        self.__get_numeric_fields()
        self.__reindex_numeric_fields(concatenation_order)
        self.scoreboard = {}
        self.patterns = {}
        self.nf_intervals = {}
        self.regex_filenames, self.regexes = {}, {}
        self.__setup_filenames()
    def __group_by_alpha(self):
        filelist = copy.deepcopy(self.fl)
        self.alphagrps = group_preliminary(filelist)
        self.grps = copy.deepcopy(self.alphagrps)
    def __get_numeric_fields(self):
        self.numfields_global = []
        for alphagrp in self.alphagrps:
            numfields = get_numeric_fields(alphagrp)
            self.numfields_global.append(numfields)
        self.numfields_original = copy.deepcopy(self.numfields_global)
        # print(self.numfields_original)
    def __reindex_numeric_fields(self, axes):
        if axes is None:
            axes = 'auto'
        axes, self.is_auto = parse_axes(axes, self.numfields_original)
        if self.fname_is_repaired:
            self.is_auto = False
        replacement = []
        for i, axpattern in enumerate(axes):
            nfield_repl = []
            nfields = copy.deepcopy(self.numfields_global[i])
            if len(nfields) == len(axpattern):
                for j, sign in enumerate(axpattern):
                    if sign == 'x':
                        nfield_repl.append([None] * len(nfields[j]))
                    else:
                        nfield_repl.append(nfields[j])
            replacement.append(nfield_repl)
        self.numfields_global = replacement
        self.concatenation_order = axes
        if self.is_auto:
            self.newDir = self.rootDir
        else:
            self.newDir = self.rootDir + '/tempdir'
    def __proofread_filenames(self): ### check if filenames contain space
        names_fixed = []
        self.fname_is_repaired = False
        for i, grp in enumerate(self.grps):
            grp_fixed = []
            for fname in grp:
                if ' ' in fname:
                    self.is_auto = False
                    self.newDir = self.rootDir + '/tempdir'
                    fname_fixed = fname.replace(' ', '-')
                    self.fname_is_repaired = True
                else:
                    fname_fixed = fname
                grp_fixed.append(fname_fixed)
            names_fixed.append(grp_fixed)
        return names_fixed
    def __setup_filenames(self):
        newgrps = self.__proofread_filenames()
        is_auto = self.is_auto
        oldDir = self.rootDir
        newDir = self.newDir
        axes = self.concatenation_order
        if not is_auto:  ### The default scenario where user chooses the automatic detection of axes.
            try:
                os.makedirs(newDir)
            except:
                pass
            for i, grp in enumerate(self.grps):
                newgrp = newgrps[i]
                newnames = _insert_dimension_specifiers(newgrp, axes[i])
                for olditem, newitem in zip(grp, newnames):
                    oldpath = os.path.join(oldDir, olditem)
                    newpath = os.path.join(newDir, newitem)
                    oldpath_abs = os.path.abspath(oldpath)
                    # print(oldpath)
                    # print(newpath)
                    os.symlink(oldpath_abs, newpath)
        filelist = os.listdir(newDir)
        fl = copy.deepcopy(filelist)
        if self.selby is not None:
            fl = [item for item in fl if self.selby in item]
        if self.rejby is not None:
            fl = [item for item in fl if not self.rejby in item]
        self.fl = sorted(fl)
        self.__group_by_alpha()
        self.__get_numeric_fields()
        self.__reindex_numeric_fields(self.concatenation_order)
    def regroup(self, grp_no, nf_no):
        numfield = self.numfields_global[grp_no][nf_no]
        numfield_ = self.numfields_original[grp_no][nf_no]
        if numfield[0] is None:
            slices = get_identity_groups(numfield_, True)
        else:
            slices = get_slices(numfield)
        score = len(slices)
        if score > 1:
            self.scoreboard[(grp_no, nf_no)] = (score, slices)
    def cycle(self):
        for i, nfgrp in enumerate(self.numfields_global):
            nfgrp = self.numfields_global[i]
            for j in range(len(nfgrp)):
                self.regroup(i, j)
    def apply_index(self): # TO BE APPLIED FOR A SINGLE ALPHAGRP
        if len(self.scoreboard) == 0:
            print("Iterations must end. No new indices found.")
            pass
        else:
            items = transpose_list(self.scoreboard.items())
            ids = items[0]
            scores, slices = transpose_list(items[1])
            score_best = min(scores)
            idx_best = scores.index(score_best)
            grp_no, numf_no = ids[idx_best]
            slcs = slices[idx_best]
            grp = self.grps[grp_no]
            numfields = self.numfields_global[grp_no]
            numfields_ = self.numfields_original[grp_no]
            sliced_numfields, sliced_numfields_, sliced_grp = [], [], []
            for slc in slcs:
                sliced_grp.append(grp[slc])
                sliced_nf_pergr = [nf[slc] for nf in numfields]
                sliced_nf_pergr_ = [nf[slc] for nf in numfields_]
                sliced_numfields.append(sliced_nf_pergr)
                sliced_numfields_.append(sliced_nf_pergr_)
            self.grps.pop(grp_no)
            self.numfields_global.pop(grp_no)
            self.numfields_original.pop(grp_no)
            axes_grp = self.concatenation_order
            axes = axes_grp[grp_no]
            self.concatenation_order.insert(grp_no, axes)
            for grp, nf, nf_ in zip(sliced_grp, sliced_numfields, sliced_numfields_):
                # print(len(self.scoreboard))
                if len(grp) > 0:
                    self.grps.insert(grp_no, grp)
                if len(nf) > 0:
                    elnum = get_elnum(nf)
                    if elnum > 0:
                        # print(elnum)
                        self.numfields_global.insert(grp_no, nf)
                        self.numfields_original.insert(grp_no, nf_)
            self.scoreboard = {}
    def group_files(self):
        for i in range(2):
            if i > 0: split_by_increments = True
            oldres = None
            while True:
                # print(split_by_increments)
                self.cycle()
                self.apply_index()
                res = len(self.grps)
                if res == oldres:
                    break
                oldres = res
        return self.grps
    ####################### Above methods divide filelist into groups. Below we create pattern files for each group using respective numeric field.
    def __get_numfield_intervals(self, grp_no):
        grp = self.grps[grp_no]
        file = grp[-1]
        numfields, numfield_intervals = [], []
        for m in re.finditer(r'\d+', file):
            zoneidx = (m.start(0), m.end(0))
            zone = file[zoneidx[0]:zoneidx[1]]
            numfield_intervals.append(zoneidx)
            numfields.append(zone)
        return numfields, numfield_intervals
    def __create_pattern_perNumfield(self, grp_no, nf_no):
        nf = sorted(copy.deepcopy(self.numfields_global[grp_no][nf_no]))
        # nf = ['00', '02', '04', '06', '00', '02', '04', '06']
        # nf = ['1349', '1349', '1349', '1349', '1349']
        # nf.sort()
        uqs, _ = find_uniques(nf)
        minvalstr = nf[0]; maxvalstr =nf[-1]
        if nf[0] is None:
            pattern = None
        elif len(nf) == 1:
            pattern = '<%s>' % maxvalstr
        elif len(uqs) > 1:
            increment = int(uqs[1]) - int(uqs[0])
            if increment > 0:
                pattern = '<%s-%s:%s>' % (minvalstr, maxvalstr, increment)
            elif increment == 0: ### THIS IS AN IMPOSSIBLE OPTION
                pattern = '<%s>' % maxvalstr
            elif increment < 0:
                print("Something is seriously wrong. Increment within a group cannot be below zero.")
        elif len(uqs) == 1:
            pattern = '<%s>' % maxvalstr
        return pattern
    def __create_patternfilename_perNumfield(self, grp_no, nf_no):
        nf = sorted(copy.deepcopy(self.numfields_global[grp_no][nf_no]))
        # nf = ['00', '02', '04', '06', '00', '02', '04', '06']
        # nf = ['1349', '1349', '1349', '1349', '1349']
        # nf.sort()
        uqs, _ = find_uniques(nf)
        minvalstr = nf[0]; maxvalstr =nf[-1]
        if nf[0] is None:
            pattern = None
        elif len(nf) == 1:
            pattern = '%s' % maxvalstr
        elif len(uqs) > 1:
            increment = int(uqs[1]) - int(uqs[0])
            if increment > 0:
                pattern = 'Range{%s-%s-%s}' % (minvalstr, maxvalstr, increment)
            elif increment == 0: ### THIS IS AN IMPOSSIBLE OPTION
                pattern = '%s' % maxvalstr
            elif increment < 0:
                print("Something is seriously wrong. Increment within a group cannot be below zero.")
        elif len(uqs) == 1:
            pattern = '%s' % maxvalstr
        return pattern
    def find_patterns(self):
        grps = self.grps
        numfields_global = self.numfields_global
        fnames = {}
        filenames = {}
        regexes = {}
        for grp_no in range(len(grps)):
            self.patterns[grp_no] = []
            fnames[grp_no] = []
            _, intervals = self.__get_numfield_intervals(grp_no)
            nfields = numfields_global[grp_no]
            self.nf_intervals[grp_no] = intervals
            for i, nfield in enumerate(nfields):
                if nfield[0] is None:
                    pattern = None
                    fname = None
                else:
                    pattern = self.__create_pattern_perNumfield(grp_no, i)
                    fname = self.__create_patternfilename_perNumfield(grp_no, i)
                fnames[grp_no].append(fname)
                self.patterns[grp_no].append(pattern)
        patterns = self.patterns
        self.fnames = fnames
        for grp_no in patterns:
            grp = grps[grp_no]
            intervals = self.nf_intervals[grp_no]
            reg = copy.deepcopy(grp[-1])
            pgrp = patterns[grp_no]
            reconst = [reg[:intervals[0][0]]]
            for i in range(1, len(intervals)):
                idx0, idx1 = intervals[i - 1]; idx2, idx3 = intervals[i]
                if pgrp[i - 1] is None:
                    reconst.append(reg[idx0:idx1])
                elif pgrp[i - 1] is not None:
                    reconst.append(pgrp[i - 1])
                reconst.append(reg[idx1:idx2])
            reconst.append(pgrp[i])
            reconst.append(reg[idx3:])
            reg = ''.join(tuple(reconst))
            regexes[grp_no] = reg
            ####################################################################
            fname = reg.replace('<', '{')
            fname = fname.replace('>', '}')
            fname = fname.replace(':', '-')
            string = fname.split('.')
            if len(string) > 1:
                string = ''.join((*string[:-1], '.pattern'))
            else:
                string = ''.join((*string, '.pattern'))
            filenames[grp_no] = string
        self.regexes = transpose_list(regexes.items())[1]
        self.regex_filenames = transpose_list(filenames.items())[1]
    def write(self):
        newDir = self.newDir
        if len(self.regexes) == 0:
            raise ValueError("No pattern files were generated.")
        for fname, reg in zip(self.regex_filenames, self.regexes):
            fpath = os.path.join(newDir, fname)
            with open(fpath, 'w') as writer:
                writer.write(reg)






# ''.join(('a', 'b'))

# fl = ['23052022_D3_ 0001.oir', '23052022_D3_ 0002.oir', '23052022_D3_0003.oir', '23052022_D3_0004.oir',
#       '23052022_D3_0005.oir', '23052022_D3_0006.oir', '23052022_D3_0007.oir', '23052022_D3_0009.oir',
#       '23052022_D3_0010.oir', '23052022_D3_0011.oir', '23052022_D3_0012.oir', '23052022_D3_0013.oir',
#       '23052022_D3_0014.oir',
#       '23052022_T26IG4_0000.oir', '23052022_T26IG4_0001.oir', '23052022_T26IG4_0002.oir','23052022_T26JG4_0002.oir',
#       '23052022_T26IG4_0003.oir', '23052022_T26IG4_0004.oir', '23052022_T26IG4_0005.oir', '23052022_T26IG4_0006.oir',
#       '23052022_T26IG4_0007.oir', '23052022_T26IG4_0008.oir', '23052022_T26IG4_0009.oir', '23052022_T26IG7_0000.oir',
#       '23052022_T26IG7_0001.oir', '23052022_T26IG7_0002.oir', '23052022_T26IG7_0004.oir', '23052022_T26IG7_0005.oir',
#       '23052022_T26IG7_0006.oir', '23052022_T26IG7_0007.oir','23052022_T26IG7_0008.oir',
#       '23052022_T26IG7_00010.oir', '23052022_T26IG7_00011.oir', '23052022_T26IG7_00012.oir']
# h = group_by_size(fl)
#
# fl.sort()
# filelist = copy.deepcopy(fl)
# items = transpose_list(grouper.scoreboard.items())
# # h = [h] * 4


# grouper.scoreboard.items()
#
# fl = os.listdir("/home/oezdemir/PycharmProjects/nfprojects/test1")

# grouper = FilelistGrouper(fl)
# /home/oezdemir/PycharmProjects/nfprojects/test2/multidimensional_sequence


#################################################################
# axes = 'auto'
# grouper = FilelistGrouper("/home/oezdemir/PycharmProjects/nfprojects/daja", concatenation_order = axes, rejby = 'Transmission')
# grps = grouper.group_files()
# grouper.find_patterns()
# grouper.write()
#################################################################



# grouper.write()

# get_slices([0, 0, 0, 0, 1, 1])

# for item in grps:
#     if '23052022_T26JG4_0002.oir' in item:
#         print(item)

# grouper.cycle()
# grouper.apply_index()

# nf = grouper.numfields_global[39][3]
# nf[slice(0, None, None)]

