#!/usr/bin/env python

import os, subprocess, argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('s3path')
    args = parser.parse_args()
    p = subprocess.Popen(["mc", "ls", args.s3path], stdout = subprocess.PIPE)
    out, err = p.communicate()
    text = out.decode('utf-8')
    llist = text.split('\n')
    final = []
    for item in llist:
        if len(item) > 0:
            if len(final) > 0:
                final.append('\n')
            lol = item.split(' ')
            while '' in lol:
                lol.remove('')
            jn = ''.join(lol[4:])
            final.append(os.path.join(args.s3path, jn))
    print(''.join(final))