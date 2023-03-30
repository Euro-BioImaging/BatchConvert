#!/usr/bin/env python
import subprocess
import argparse
import json
import os
import sys
import re

intlist = lambda s: [int(x) for x in re.findall(r'\b\d+\b', s)]

if __name__ == '__main__':
    scriptpath = os.path.dirname(os.path.realpath(__file__)) # /home/oezdemir/PycharmProjects/nfprojects/bftools/modules/templates
    os.chdir(scriptpath) #
    os.chdir('..') # /home/oezdemir/PycharmProjects/nfprojects/bftools ### note that this is the execution directory.
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    # print("args are %s" % args)
    with open('./params/params.json', 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = parser.parse_args(namespace=t_args)
        # print(args)
    # keys = args.__dict__.keys()
    cmd = ["#!/usr/bin/env bash\n"]
    keys = args.__dict__.keys()
    if args.output_type == 'ometiff':
        cmd += ["bfconvert"]
        if "noflat" in keys:
            cmd += [" -noflat"]
        if "series" in keys:
            cmd += [" -series", ' %s' % args.series]
        if "timepoint" in keys:
            cmd += [" -timepoint", ' %s' % args.timepoint]
        if "channel" in keys:
            cmd += [" -channel", ' %s' % args.channel]
        if "z_slice" in keys:
            cmd += [" -z", ' %s' % args.z_slice]
        if "range" in keys:
            _range = intlist(args.range)
            if len(_range) != 2:
                raise TypeError('Range must have two integers specifying first and last indices of images.')
            else:
                cmd += [" -range"]
                for i in _range:
                    cmd += [' %s' % i]
        if "autoscale" in keys:
            cmd += [" -autoscale"]
        if "crop" in keys:
            _crop = ''.join(args.crop[1:-1].split(' '))
            cmd += [" -crop", ' %s' % _crop]
        if "compression_tiff" in keys:
            cmd += [" -compression", ' %s' % args.compression_tiff]
        if "resolution_scale" in keys:
            cmd += [" -pyramid-scale", ' %s' % args.resolution_scale]
        if "resolutions_tiff" in keys:
            cmd += [" -pyramid-resolutions", ' %s' % args.resolutions_tiff]
        # add here all params
        cmd.append(' %s' % "$1")
        cmd.append(' %s' % "$2")
        cmdstr = ''.join(cmd)
        sys.stdout.write(cmdstr)
    elif args.output_type == 'omezarr':
        cmd += ["bioformats2raw"]
        if "resolutions_zarr" in keys:
            cmd += [" --resolutions", ' %s' % args.resolutions_zarr]
        if "chunk_h" in keys:
            cmd += [" --tile_height", ' %s' % args.chunk_h]
        if "chunk_w" in keys:
            cmd += [" --tile_width", ' %s' % args.chunk_w]
        if "chunk_d" in keys:
            cmd += [" --chunk_depth", ' %s' % args.chunk_d]
        if "downsample_type" in keys:
            cmd += [" --downsample-type", ' %s' % args.downsample_type]
        if "compression_zarr" in keys:
            cmd += [" --compression", ' %s' % args.compression_zarr]
        if "max_workers" in keys:
            cmd += [" --max_workers", ' %s' % args.max_workers]
        if "no_nested" in keys:
            cmd += [" --no-nested"]
        if "drop_series" in keys:
            cmd += [" --scale-format-string", ' %s' % "'%2$d'"]
        if "overwrite" in keys:
            cmd += [" --overwrite"]
        cmd.append(' %s' % "$1")
        cmd.append(' %s' % "$2")
        cmdstr = ''.join(cmd)
        sys.stdout.write(cmdstr)
        # os.chdir(scriptpath)
        # subprocess.run(cmd)




