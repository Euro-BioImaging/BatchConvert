#!/usr/bin/env python
import os
import pandas as pd
import numpy as np
import shutil

mask_func = lambda x: len(np.unique(x)) == 1

def _separate_groups(series):
    if not isinstance(series, type([])):
        try:
            series = list(series)
        except:
            raise TypeError('Input cannot be converted into a list type.')
    assert isinstance(series, type([]))
    series.sort()
    groups = []
    group = []
    for i in range(1, len(series)):
        col0 = series[i - 1]
        col1 = series[i]
        if col1 - col0 == 1:
            group.append(col0)
        else:
            if (col0 - 1) in group:
                group.append(col0)
                groups.append(group)
                group = []
            else:
                groups.append([col0])
    if (col1 - 1) in group:
        group.append(col1)
        groups.append(group)
        group = []
    else:
        groups.append([col1])
    return groups

def _aggregate_group(group):
    arr = group.to_numpy().astype(int)
    columns = list(group.columns)
    cols = np.array(columns)
    powers = np.power(10, np.arange(len(cols)))[::-1]
    powers = powers.reshape(1, -1)
    aggregated = (arr * powers).sum(axis = 1)
    newgroup = group.copy(deep = True)
    newgroup.iloc[:, :-1] = None
    newgroup.iloc[:, -1] = aggregated
    return newgroup

def _aggregate_groups(df):
    columns = df.columns
    groups = _separate_groups(columns)
    parts = [df.loc[:, tuple(gr)] for gr in groups]
    parts_aggregated = [_aggregate_group(gr) for gr in parts]
    concatted = pd.concat(parts_aggregated, axis = 1)
    return concatted

# agg = _aggregate_groups(nonmatch)

class PatternHandler:
    def __init__(self, rootDir, force_pattern = None):
        filenames = os.listdir(rootDir)
        filenames.sort()
        df_rootDir = pd.DataFrame([list(item) for item in filenames])
        self.rootDir = rootDir
        self.filenames = filenames
        self.df_rootDir = df_rootDir
        self.forced_pattern = force_pattern
    def _infer_pattern(self): ### DETECT ALSO MULTIPLE DIMENSIONALITIES, NOT JUST ONE
        df = self.df_rootDir
        # df = df_rootDir
        pattern_mask = df.apply(mask_func, axis = 0)
        nonmatch = df.loc[:, pattern_mask == False]
        nonmatch = _aggregate_groups(nonmatch)
        nonmatch_mins = nonmatch.min(axis = 0)
        nonmatch_maxs = nonmatch.max(axis = 0)
        masked = df.loc[:, pattern_mask]
        for i in nonmatch.columns:
            idx0 = nonmatch_mins[i]
            idx1 = nonmatch_maxs[i]
            if idx0 is None and idx1 is None:
                reg = ''
            else:
                idx1 = str(idx1)
                idx0 = str(idx0)
                for j in range(len(idx1)):
                    if len(idx1) == len(idx0):
                        break
                    else:
                        idx0 = '0' + idx0
                reg = '<%s-%s>' % (''.join(idx0), ''.join(idx1))
            masked[i] = reg
        masked_sorted = masked.T.sort_index().T
        filename_list = masked_sorted.loc[0].to_numpy().tolist()
        filename = ''.join(filename_list)
        return filename
    def _insert_pattern(self, patterns):
        df = self.df_rootDir
        if isinstance(patterns, type('')):
            patterns = [patterns]
        ###
        df_newDir = df.copy(deep = True)
        ###
        pattern_mask = df.apply(mask_func, axis = 0)
        nonmatch = df.loc[:, pattern_mask == False]
        nonmatch = _aggregate_groups(nonmatch)
        ct_valid_columns = 0
        for i in nonmatch.columns:
            if nonmatch.loc[0, i] is not None:
                ct_valid_columns += 1
        assert len(patterns) == ct_valid_columns, 'Number of given patterns must match number of varying text fields in the filenames'
        nonmatch_mins = nonmatch.min(axis = 0)
        nonmatch_maxs = nonmatch.max(axis = 0)
        masked = df.loc[:, pattern_mask]
        df_newDir = masked.copy()
        idx = 0
        for i in nonmatch.columns:
            idx0 = nonmatch_mins[i]
            idx1 = nonmatch_maxs[i]
            if idx0 is None and idx1 is None:
                reg = ''
            else:
                idx1 = str(idx1)
                idx0 = str(idx0)
                for j in range(len(idx1)):
                    if len(idx1) == len(idx0):
                        break
                    else:
                        idx0 = '0' + idx0
                idx_infile = []
                for item in nonmatch[i]:
                    itemstr = str(item)
                    for j in range(len(idx1)):
                        if len(idx1) == len(itemstr):
                            pass
                        else:
                            itemstr = '0' + itemstr
                    idx_infile.append(itemstr)
                reg = '%s<%s-%s>' % (patterns[idx], ''.join(idx0), ''.join(idx1))
                df_newDir[i] = [patterns[idx] + item for item in idx_infile]
                idx += 1
            masked[i] = reg
        masked_sorted = masked.T.sort_index().T
        df_newDir_sorted = df_newDir.T.sort_index().T
        filename_list = masked_sorted.loc[0].to_numpy().tolist()
        filename = ''.join(filename_list)
        return df_newDir_sorted, filename

    def dump_inferred_pattern(self):
        rootDir = self.rootDir
        pattern_file = self._infer_pattern()
        with open(rootDir + '/new.pattern', 'w') as writer:
            writer.write(pattern_file)

    def dump_inserted_pattern(self, patterns):
        rootDir = self.rootDir
        df_rootDir = self.df_rootDir
        df_newDir, pattern_file = self._insert_pattern(patterns)
        newDir = rootDir + '/tempdir'
        try:
            os.makedirs(newDir)
        except:
            pass
        lol_rootDir = df_rootDir.to_numpy().tolist()
        lol_newDir = df_newDir.to_numpy().tolist()
        for olditem, newitem in zip(lol_rootDir, lol_newDir):
            oldfile = ''.join(olditem)
            newfile = ''.join(newitem)
            oldpath = os.path.join(rootDir, oldfile)
            newpath = os.path.join(newDir, newfile)
            shutil.copy(oldpath, newpath)
        with open(newDir + '/new.pattern', 'w') as writer:
            writer.write(pattern_file)

