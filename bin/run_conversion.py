#!/usr/bin/env python
import shlex
import subprocess
import argparse
import json
import os
import sys
import re

intlist = lambda s: [int(x) for x in re.findall(r'\b\d+\b', s)]

if __name__ == '__main__':
    homepath = os.environ.get('HOMEPATH')
    temppath = os.environ.get('TEMPPATH')
    parampath = os.environ.get('PARAMPATH')
    defparamfile = os.path.join(parampath, 'params.json.default')
    backupparamfile = os.path.join(parampath, 'params.json.backup')
    paramfile = os.path.join(parampath, 'params.json')

    parser = argparse.ArgumentParser()
    parser.add_argument('input_path')
    parser.add_argument('output_path')

    # print("args are %s" % args)
    with open(paramfile, 'rt') as f:
        t_args = argparse.Namespace()
        t_args.__dict__.update(json.load(f))
        args = parser.parse_args(namespace=t_args)
    # inps = args.input_path.replace("\ ", " ")
    # outs = args.output_path.replace("\ ", " ")
    inps = args.input_path
    outs = args.output_path

    cmd = []
    keys = args.__dict__.keys()
    if not os.path.isfile(inps):
        with open(outs, mode = 'w') as writer:
            writer.write(inps)
    else:
        if args.output_type == 'ometiff':
            cmd += ["bfconvert"]
            if "noflat" in keys:
                cmd += ["-noflat"]
            if "series" in keys:
                cmd += ["-series", '%s' % args.series]
            if "timepoint" in keys:
                cmd += ["-timepoint", '%s' % args.timepoint]
            if "channel" in keys:
                cmd += ["-channel", '%s' % args.channel]
            if "z_slice" in keys:
                cmd += ["-z", '%s' % args.z_slice]
            if "range" in keys:
                _range = intlist(args.range)
                if len(_range) != 2:
                    raise TypeError('Range must have two integers specifying first and last indices of images.')
                else:
                    cmd += ["-range"]
                    for i in _range:
                        cmd += ['%s' % i]
            if "autoscale" in keys:
                cmd += ["-autoscale"]
            if "crop" in keys:
                _crop = ''.join(args.crop[1:-1].split(' '))
                cmd += ["-crop", '%s' % _crop]
            if "compression_tiff" in keys:
                cmd += ["-compression", '%s' % args.compression_tiff]
            if "resolution_scale" in keys:
                cmd += ["-pyramid-scale", '%s' % args.resolution_scale]
            if "resolutions_tiff" in keys:
                cmd += ["-pyramid-resolutions", '%s' % args.resolutions_tiff]
            # add here all params
            cmd.append(f"{inps}")
            cmd.append(f"{outs}")
            # cmdstr = ''.join(cmd)
            print(cmd)
            # sys.stdout.write(cmdstr)
            subprocess.run(cmd, shell = False)
        elif args.output_type == 'omezarr':
            cmd += ["bioformats2raw"]
            if "min_xy_size" in keys:
                cmd += ["--target-min-size", '%s' % args.min_xy_size]
            if "resolutions_zarr" in keys:
                cmd += ["--resolutions", '%s' % args.resolutions_zarr]
            if "chunk_y" in keys:
                cmd += ["--tile_height", '%s' % args.chunk_y]
            if "chunk_x" in keys:
                cmd += ["--tile_width", '%s' % args.chunk_x]
            if "chunk_z" in keys:
                cmd += ["--chunk_depth", '%s' % args.chunk_z]
            if "downsample_type" in keys:
                cmd += ["--downsample-type", '%s' % args.downsample_type]
            if "compression_zarr" in keys:
                cmd += ["--compression", '%s' % args.compression_zarr]
            if "max_workers" in keys:
                cmd += ["--max_workers", '%s' % args.max_workers]
            if "no_nested" in keys:
                if args.no_nested in (True, "True"):
                    cmd += ["--no-nested"]
                elif args.no_nested in (False, "False", None, "None"):
                    pass
                else:
                    raise ValueError(f"--no-nested cannot have the value {args.no_nested}")
            if "drop_series" in keys:
                if args.drop_series in (True, "True"):
                    val = '%2$d'
                    cmd += ["--scale-format-string", val]
                elif args.drop_series in (False, "False", None, "None"):
                    pass
                else:
                    raise ValueError(f"--drop_series cannot have the value {args.drop_series}")
            if "overwrite" in keys:
                cmd += ["--overwrite"]
            cmd.append(f"{inps}")
            cmd.append(f"{outs}")
            # cmdstr = ''.join(cmd)
            print(cmd)
            # sys.stdout.write(cmdstr)
            subprocess.run(cmd, shell = False)




