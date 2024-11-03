#!/usr/bin/env python

import os, subprocess, argparse


def listpaths(s3path,
              contains = None,
              excludes = None
              ):
    basename = os.path.basename(s3path)
    dirname = os.path.dirname(s3path)
    if not dirname.endswith('/'):
        dirname = dirname + '/'
    # command = ['mc', "-C", "./mc", "find", dirname, "--name", basename]
    if basename == '**':
        command = ['mc', "-C", "./mc", "find", dirname]
    elif basename == '*':
        command = ['mc', "-C", "./mc", "find", dirname, "--maxdepth", "1"]
    elif '**' in basename:
        command = ['mc', "-C", "./mc", "find", dirname, "--name", basename, "--maxdepth", "0"]
    elif '*' in basename:
        command = ['mc', "-C", "./mc", "find", dirname, "--name", basename, "--maxdepth", "1"]
    else:
        command = ['mc', "-C", "./mc", "find", s3path, "--maxdepth", "2"]
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True
                         )
    out, err = p.communicate()
    # text = out.decode('utf-8')
    llist = out.split('\n')
    final = []
    for item in llist:
        if (item == s3path) | len(item) == 0:
            continue
        elif item[:-1] == s3path:
            continue
        elif item[-1] == '/': # exclude directories
            continue
        else:
            if contains not in (None, "None", ""):
                if contains not in os.path.basename(item):
                    continue
            if excludes not in (None, "None", ""):
                if excludes in os.path.basename(item):
                    continue
        if len(final) > 0:
            final.append('\n')
        final.append(item)
    return final


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('s3path')
    parser.add_argument('--contains', default="")
    parser.add_argument('--excludes', default="")
    args = parser.parse_args()
    # p = subprocess.Popen(["mc", "-C", "./mc", "tree", "--depth", "1", "--files", args.s3path], stdout = subprocess.PIPE)
    s3path = args.s3path
    if s3path.endswith('/'):
        s3path = s3path[:-1]
    s3path = s3path.replace(" ", "*")
    llist = listpaths(s3path, contains = args.contains, excludes=args.excludes)
    print(''.join(llist))
