#!/usr/bin/env python
import os
import argparse
from PatternHandler import save_pattern_file

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('input_path')
    parser.add_argument('--concatenation_order', default = 'infer_from_filenames')

    args = parser.parse_args()

    rootDir = args.input_path
    conc_order = args.concatenation_order
    filenames = os.listdir(rootDir)
    pattern_file = None
    for filename in filenames:
        if filename.endswith('pattern'):
            pattern_file = filename
            print('Existing pattern file found')
            break

    if pattern_file is None:
        if pattern_file == 'infer_from_filenames':
            save_pattern_file(rootDir)
        else:
            save_pattern_file(rootDir, conc_order)

