#!/usr/bin/env python

import os, subprocess, argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('s3path')
    args = parser.parse_args()
    # p = subprocess.Popen(["mc", "-C", "./mc", "tree", "--depth", "1", "--files", args.s3path], stdout = subprocess.PIPE)
    s3path = args.s3path
    # s3path = "s3/eosc-future/test01"
    if s3path.endswith('/'):
        s3path = s3path[:-1]
    # s3path = "test01/*.jpg"
    s3path = s3path.replace(" ", "*")
    p = subprocess.Popen(['mc', "-C", "./mc", "find", s3path],
                         stdout = subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True
                         )
    out, err = p.communicate()
    # text = out.decode('utf-8')
    llist = out.split('\n')
    if len(llist[0]) == 0:
        basename = os.path.basename(s3path)
        dirname = os.path.dirname(s3path)
        p = subprocess.Popen(['/home/oezdemir/executables/bin/mc', "-C", "./mc", "find", dirname, "--name", basename],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True
                             )
        out, err = p.communicate()
        # text = out.decode('utf-8')
        llist = out.split('\n')
    # print(llist)
    final = []
    for item in llist:
        if (item == s3path) | (item[:-1] == s3path):
            continue
        if len(item) > 0:
            if len(final) > 0:
                final.append('\n')
            final.append(item)
    print(''.join(final))
