#!/usr/bin/env python
import subprocess
import argparse
import os, sys, shutil
import json

def intlist(s):
    rv = []
    for x in s.split(','):
        try:
            x = int(x)
        except ValueError:
            raise TypeError("Non-integer parameter {x}" % (x,))
        rv.append(x)
    return rv

bf2rawParams = { "resolutions_zarr": "Number of resolution levels in the OME-Zarr pyramid. Enter an integer value.",
                 "chunk_h": "Chunk height. Enter an integer value.",
                 "chunk_w": "Chunk width. Enter an integer value.",
                 "chunk_d": "Chunk depth. Enter an integer value.",
                 "downsample_type": "Downsampling algorithm.\nOptions are: SIMPLE, GAUSSIAN, AREA, LINEAR, CUBIC, LANCZOS",
                 "compression_zarr": "Compression algorithm.\nOptions are: null, zlib, blosc",
                 "max_workers": "Number of workers. Enter an integer value.",
                 "no_nested": "Whether to organise the chunk files in a flat directory.\nOptions are: True, False",
                 "drop_series": "Whether to drop the series hierarchy from the OME-Zarr.\nOptions are: True, False",
                 "dimension_order": "Order of dimensions. It is advised to stay with the input dimensions. To do so, enter 'skip' or 's'.\nOptions are: XYZCT, XYZTC, XYCTZ, XYCZT, XYTCZ, XYTZC",
                 "overwrite": "Whether to overwrite any existing files in the output path.\nOptions are: True, False"
                }
bftoolsParams = ["noflat", "series", "timepoint", "channel", "z_slice", "range",
                  "autoscale", "crop", "compression_tiff", "resolutions_tiff",
                 'resolution_scale']
# common = set([item for item in bftoolsParams + bf2rawParams if item in bftoolsParams and item in bf2rawParams])
bf2raw_params = [item for item in bf2rawParams if not item in bftoolsParams]
bftools_params = [item for item in bftoolsParams if not item in bf2rawParams]
s3_params = ["S3REMOTE", "S3ENDPOINT", "S3ACCESS", "S3SECRET", "S3BUCKET"]
bia_params = ["BIA_REMOTE"]
slurm_params = ["queue_size", "submit_rate_limit", "cluster_options", "time"]

if __name__ == "__main__":
    relpath = os.getcwd()
    scriptpath = os.path.dirname(os.path.realpath(__file__)) # /home/oezdemir/PycharmProjects/nfprojects/bftools/modules/templates
    os.chdir(scriptpath)

    with open("../params/params.json.default", 'r+') as f:
        jsonfileparams = json.load(f)
    defparams = dict(jsonfileparams)
    defkeys = defparams.keys()
    getdef = lambda key, default: defparams[key] if key in defkeys else default

    parser = argparse.ArgumentParser()
    #####################################################################################################
    ################################## CONFIGURATION SUBPARSERS #########################################
    #####################################################################################################
    subparsers = parser.add_subparsers()
    configure_s3_remote = subparsers.add_parser('configure_s3_remote')
    configure_s3_remote.add_argument('--remote', default=None)
    configure_s3_remote.add_argument('--url', default=None)
    configure_s3_remote.add_argument('--access', default=None)
    configure_s3_remote.add_argument('--secret', default=None)
    configure_s3_remote.add_argument('--bucket', default=None)
    configure_bia_remote = subparsers.add_parser('configure_bia_remote')
    configure_bia_remote.add_argument('--secret_dir', default=None)
    configure_ometiff = subparsers.add_parser('configure_ometiff')
    configure_ometiff.add_argument('--noflat', default = None)
    configure_ometiff.add_argument('--series', default = None)
    configure_ometiff.add_argument('--timepoint', default = None)
    configure_ometiff.add_argument('--channel', default = None)
    configure_ometiff.add_argument('--z_slice', default = None)
    configure_ometiff.add_argument('--range', default = None)
    configure_ometiff.add_argument('--autoscale', default = None)
    configure_ometiff.add_argument('--crop', default = None)
    configure_ometiff.add_argument('--compression_tiff', default = None)
    configure_ometiff.add_argument('--resolutions_tiff', default = None)
    configure_ometiff.add_argument('--resolution_scale', default = None)
    configure_omezarr = subparsers.add_parser('configure_omezarr')
    configure_omezarr.add_argument('--resolutions_zarr', default = None)
    configure_omezarr.add_argument('--chunk_h', default = None)
    configure_omezarr.add_argument('--chunk_w', default = None)
    configure_omezarr.add_argument('--chunk_d', default = None)
    configure_omezarr.add_argument('--downsample_type', default = None)
    configure_omezarr.add_argument('--compression_zarr', default = None)
    configure_omezarr.add_argument('--max_workers', default = None)
    configure_omezarr.add_argument('--no_nested', default = None)
    configure_omezarr.add_argument('--drop_series', default = None)
    configure_omezarr.add_argument('--dimension_order', default = None)
    configure_omezarr.add_argument('--overwrite', default = None)
    configure_slurm = subparsers.add_parser('configure_slurm')
    configure_slurm.add_argument('--queue_size', default = None)
    configure_slurm.add_argument('--submit_rate_limit', default = None)
    configure_slurm.add_argument('--cluster_options', default = None)
    configure_slurm.add_argument('--time', default = None)
    #####################################################################################################
    ##################################### CONVERSION SUBPARSERS #########################################
    #####################################################################################################
    ometiff = subparsers.add_parser('ometiff')
    ### add io parameters - obligatory
    ometiff.add_argument('in_path', default=getdef('in_path',
                                                   "placehold"))  # you can update existing arguments with those from json file
    ometiff.add_argument('out_path', default=getdef('out_path', "placehold"))
    ometiff.add_argument('--pattern', '-p', default=getdef('pattern', ""), type=str)
    ometiff.add_argument('--reject_pattern', '-rp', default=getdef('reject_pattern', ""), type=str)

    ### specify whether the input files should be concatenated into a single ome-tiff file
    ometiff.add_argument('--merge_files', default=getdef("merge_files", False), action='store_true')
    ometiff.add_argument('--concatenation_order', default=getdef("concatenation_order", 'auto'))

    ### specify the config profile
    ometiff.add_argument('--profile', '-pf', default=getdef('profile', "standard"), type=str,
                         help="Specifies one of the three profiles: standard, no_container and cluster")
    ### specify output type: if the output type is ometiff add the following parameters
    ometiff.add_argument('--noflat', '-nf', default=getdef('noflat', False), action='store_true')
    ometiff.add_argument('--series', '-s', default=getdef('series', None), type=int,
                         help='Specifies series to be converted in the input file')
    ometiff.add_argument('--timepoint', '-tp', default=getdef('timepoint', None), type=int,
                         help='Specifies timepoint to be converted in the input file')
    ometiff.add_argument('--channel', '-chn', default=getdef('channel', None), type=int,
                         help='Specifies channel to be converted in the input file')
    ometiff.add_argument('--z_slice', '-z', default=getdef('z_slice', None), type=int,
                         help='Specifies z-slice to be converted in the input file')
    ometiff.add_argument('--range', '-r', default=getdef('range', None), type=intlist,
                         help='Specifies a range of images to be converted in the input file')
    ometiff.add_argument('--autoscale', '-as', default=getdef('autoscale', False), action='store_true',
                         help='Autoscales gray value range')
    ometiff.add_argument('--crop', '-cr', default=getdef('crop', None), type=intlist,
                         help='Crops image to region defined by given values that correspond to X, Y, width, height')
    ometiff.add_argument('--compression_tiff', '-ctiff', default=getdef('compression_tiff', None), type=str,
                         help='Specifies compression algorithm for bfconvert')
    ometiff.add_argument('--resolutions_tiff', '-rt', default=getdef('resolutions_tiff', None), type=int,
                         help='Specifies resolution levels of the pyramidal image for bfconvert. Defaults to 1')
    ometiff.add_argument('--resolution_scale', '-rs', default=getdef('resolution_scale', None), type=int,
                         help='Specifies the scale with which successive resolution level is calculated')
    ### Specify the input and output locations (source_type or dest_type): currently either local or s3
    ometiff.add_argument('--source_type', '-st', default=getdef('source_type', "local"),
                         help='Specifies where the input dataset is located: either local or s3.')
    ometiff.add_argument('--dest_type', '-dt', default=getdef('dest_type', "local"),
                         help='Specifies where the output is to be deposited: either local or s3')
    ### add s3 parameters if either of the source_type or dest_type is s3
    ometiff.add_argument('--S3REMOTE', default=getdef('S3REMOTE', "s3"))
    ometiff.add_argument('--S3ENDPOINT', default=getdef('S3ENDPOINT', "https://s3.embl.de"))
    ometiff.add_argument('--S3BUCKET', default=getdef('S3BUCKET', "eosc-future"))
    # ometiff.add_argument('--S3PATH', default="nextflowPath")
    ometiff.add_argument('--S3ACCESS', default=getdef('S3ACCESS', "eosc-future-user"))
    ometiff.add_argument('--S3SECRET', default=getdef('S3SECRET', "w2xx9EatWwmtsrbewt3LEfiGB"))
    ### add s3 parameters if either of the source_type or dest_type is BioImage Archive
    ometiff.add_argument('--BIA_REMOTE', default=getdef('BIA_REMOTE', "/17/596fcf-661c-4ed4-af91-c2354e7213e9-a24550"))
    ometiff.add_argument('--queue_size', default = getdef('queue_size', '50'))
    ometiff.add_argument('--submit_rate_limit', default = getdef('submit_rate_limit', '10/2min'))
    ometiff.add_argument('--cluster_options', default = getdef('cluster_options', '--mem-per-cpu=3140 --cpus-per-task=16'))
    ometiff.add_argument('--time', default = getdef('time', '6h'))

    omezarr = subparsers.add_parser('omezarr')
    omezarr.add_argument('in_path', default=getdef('in_path',
                                                   "placehold"))  # you can update existing arguments with those from json file
    omezarr.add_argument('out_path', default=getdef('out_path', "placehold"))
    omezarr.add_argument('--pattern', '-p', default=getdef('pattern', ""), type=str)
    omezarr.add_argument('--reject_pattern', '-rp', default=getdef('reject_pattern', ""), type=str)

    ### specify whether the input files should be concatenated into a single ome-tiff folder
    omezarr.add_argument('--merge_files', default=getdef("merge_files", False), action='store_true')
    omezarr.add_argument('--concatenation_order', default=getdef("concatenation_order", 'auto'))

    ### specify the config profile
    omezarr.add_argument('--profile', '-pf', default=getdef('profile', "standard"), type=str,
                         help="Specifies one of the three profiles: standard, no_container and cluster")

    ### If the output_type is omezarr, add the following parameters of conversion into omezarr format:
    omezarr.add_argument('--resolutions_zarr', '-rz', default=getdef('resolutions_zarr', None), type=int,
                         help='Specifies resolution levels of the pyramidal image for bioformats2raw.')
    omezarr.add_argument('--chunk_h', '-ch', default=getdef('chunk_h', None), type=int, help='Specifies chunk height')
    omezarr.add_argument('--chunk_w', '-cw', default=getdef('chunk_w', None), type=int, help='Specifies chunk width')
    omezarr.add_argument('--chunk_d', '-cd', default=getdef('chunk_d', None), type=int, help='Specifies chunk depth')
    omezarr.add_argument('--downsample_type', default=getdef('downsample_type', None), type=str,
                         help='Specifies downsampling algorithm')
    # omezarr.add_argument('--compression_tiff', '-ctiff', default=getdef('compression_tiff', None), type=str,
    #                     help='Specifies compression algorithm for bfconvert')
    omezarr.add_argument('--compression_zarr', '-czarr', default=getdef('compression_zarr', None), type=str,
                         help='Specifies compression algorithm for bioformats2raw')
    omezarr.add_argument('--max_workers', default=getdef('max_workers', None), type=int,
                         help='Specifies maximum number of processors used')
    omezarr.add_argument('--no_nested', default=getdef('no_nested', False), action='store_true',
                         help='Specifies path type.')
    omezarr.add_argument('--drop_series', default=getdef('drop_series', False), action='store_true',
                         help='Drops the series level from the hierarchy.')
    omezarr.add_argument('--dimension_order', default=getdef('dimension_order', None), type=str,
                         help='Specifies path type.')
    omezarr.add_argument('--overwrite', default=getdef('overwrite', False), action='store_true',
                         help='Overwrites the output path.')
    ### If the output_type is ometiff, add the following parameters of conversion into ometiff format: yet none
    ### Specify the input and output locations (source_type or dest_type): currently either local or s3
    omezarr.add_argument('--source_type', '-st', default=getdef('source_type', "local"),
                         help='Specifies where the input dataset is located: either local or s3.')
    omezarr.add_argument('--dest_type', '-dt', default=getdef('dest_type', "local"),
                         help='Specifies where the output is to be deposited: either local or s3')
    ### add s3 parameters if either of the source_type or dest_type is s3
    omezarr.add_argument('--S3REMOTE', default=getdef('S3REMOTE', "s3"))
    omezarr.add_argument('--S3ENDPOINT', default=getdef('S3ENDPOINT', "https://s3.embl.de"))
    omezarr.add_argument('--S3BUCKET', default=getdef('S3BUCKET', "eosc-future"))
    # omezarr.add_argument('--S3PATH', default="nextflowPath")
    omezarr.add_argument('--S3ACCESS', default=getdef('S3ACCESS', "eosc-future-user"))
    omezarr.add_argument('--S3SECRET', default=getdef('S3SECRET', "w2xx9EatWwmtsrbewt3LEfiGB"))
    ### add s3 parameters if either of the source_type or dest_type is BioImage Archive
    omezarr.add_argument('--BIA_REMOTE', default=getdef('BIA_REMOTE', "/17/596fcf-661c-4ed4-af91-c2354e7213e9-a24550"))
    omezarr.add_argument('--queue_size', default = getdef('queue_size', '50'))
    omezarr.add_argument('--submit_rate_limit', default = getdef('submit_rate_limit', '10/2min'))
    omezarr.add_argument('--cluster_options', default = getdef('cluster_options', '--mem-per-cpu=3140 --cpus-per-task=16'))
    omezarr.add_argument('--time', default = getdef('time', '6h'))
    # print(subparsers.choices.keys())
    #####################################################################################################
    #################################### RESET DEFAULTS SUBPARSER #######################################
    #####################################################################################################
    reset = subparsers.add_parser('reset_defaults')

    args = parser.parse_args()
    keys = args.__dict__.keys()
    # for item in keys:
    #     print("%s: %s" % (item, args.__dict__[item]))
    if (len(sys.argv) <= 1):
        raise ValueError('The first argument of batchconvert must be either of: \n"ometiff"\n"omezarr"\n"configure_ometiff"\n"configure_omezarr"\n"configure_bia_remote"\n"configure_s3_remote"\n"configure_slurm"\n"reset_defaults"')
        exit()
    elif sys.argv[1] not in ["ometiff", "omezarr", "configure_ometiff", "configure_omezarr", "configure_bia_remote", "configure_s3_remote", "configure_slurm", "reset_defaults"]:
        raise ValueError('The first argument of batchconvert must be either of: \n"ometiff"\n"omezarr"\n"configure_ometiff"\n"configure_omezarr"\n"configure_bia_remote"\n"configure_s3_remote"\n"configure_slurm"\n"reset_defaults"')
        exit()
    prompt = str(sys.argv[1])
    # print(sys.argv[1])
    # print(subparsers)
    # print(keys)
    if prompt == 'configure_s3_remote':
        remote_prompt = 'enter remote name (for example s3)\nEnter "skip" or "s" if you would like to keep the current value\n'
        url_prompt = 'enter url:\nEnter "skip" or "s" if you would like to keep the current value\n'
        access_prompt = 'enter access key:\nEnter "skip" or "s" if you would like to keep the current value\n'
        secret_prompt = 'enter secret key:\nEnter "skip" or "s" if you would like to keep the current value\n'
        bucket_prompt = 'enter bucket name:\nEnter "skip" or "s" if you would like to keep the current value\n'
        if args.remote is None:
            args.remote = input(remote_prompt)
        if args.url is None:
            args.url = input(url_prompt)
        if args.access is None:
            args.access = input(access_prompt)
        if args.secret is None:
            args.secret = input(secret_prompt)
        if args.bucket is None:
            args.bucket = input(bucket_prompt)
        # print(args)
        with open(os.path.join(scriptpath,  '..', 'params', 'params.json.default'), 'r+') as f:
            jsonfile = json.load(f)
            # jsondict = dict(jsonfile)
            for i, (_, value) in enumerate(args.__dict__.items()):
                key = s3_params[i]
                if (value == 's') | (value == 'skip'):
                    pass
                elif len(value) == 0:
                    try:
                        del jsonfile[key]
                    except:
                        pass
                elif len(value) > 0:
                    # print(key, value)
                    jsonfile[key] = value
            # print(jsonfile)
            f.seek(0)
            json.dump(jsonfile, f, indent = 2)
            f.truncate()
        # print("Configuration of the default s3 credentials is complete")
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('configured_s3')
        #sys.stdout.write('configured_s3') ### VERY IMPORTANT STEP
    elif prompt == 'configure_bia_remote':
        secret_dir_prompt = 'enter the secret directory for your BioStudies user space:\n'
        if args.secret_dir is None:
            args.secret_dir = input(secret_dir_prompt)
        with open(os.path.join(scriptpath, '..', 'params', 'params.json.default'), 'r+') as f:
            jsonfile = json.load(f)
            jsonfile['BIA_REMOTE'] = args.secret_dir
            f.seek(0)
            json.dump(jsonfile, f, indent=2)
            f.truncate()
        # print("Configuration of the default bia credentials is complete")
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('configured_bia')
        #sys.stdout.write('configured_bia') ### VERY IMPORTANT STEP
    elif prompt == 'configure_slurm':
        # print(prompt)
        argsdict = args.__dict__
        # print(argsdict)
        with open(os.path.join(scriptpath, '..', 'params', 'params.json.default'), 'r+') as f:
            jsonfile = json.load(f)
            for key in slurm_params:
                current = jsonfile[key]
                value = argsdict[key]
                # print(value)
                if value is None:
                    keyprompt = input('Please enter value for %s\nClick enter to set the parameter to the initial defaults\nEnter "skip" or "s" if you would like to keep the current value ´%s´\n' % (key,current))
                    # print(keyprompt)
                    if keyprompt is None:
                        pass
                    else:
                        args.__dict__[key] = keyprompt
        # with open(os.path.join(scriptpath,  '..', 'params', 'params.json.default'), 'r+') as f:
        #     jsonfile = json.load(f)
            for key, value in args.__dict__.items():
                if (value == 's') | (value == 'skip'):
                    pass
                elif len(value) == 0:
                    try:
                        del jsonfile[key]
                    except:
                        pass
                elif len(value) > 0:
                    jsonfile[key] = value
            f.seek(0)
            json.dump(jsonfile, f, indent=2)
            f.truncate()
        # print("Configuration of the default parameters for slurm is complete")
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('configured_slurm')
    elif prompt == 'configure_ometiff':
        # print(prompt)
        argsdict = args.__dict__
        # print(argsdict)
        with open(os.path.join(scriptpath,  '..', 'params', 'params.json.default'), 'r+') as f:
            jsonfile = json.load(f)
            for key in bftoolsParams:
                value = argsdict[key]
                try:
                    current = jsonfile[key]
                except:
                    current = "<bfconvert defaults>"
                # print(value)
                if value is None:
                    keyprompt = input('Please enter value for %s\nClick enter to set the parameter to the initial defaults\nEnter "skip" or "s" if you would like to keep the parameter´s current value, which is %s\n' % (key, current))
                    # print(keyprompt)
                    if keyprompt is None:
                        pass
                    else:
                        args.__dict__[key] = keyprompt
            for key, value in args.__dict__.items():
                if (value == 's') | (value == 'skip'):
                    pass
                elif len(value) == 0:
                    try:
                        del jsonfile[key]
                    except:
                        pass
                elif len(value) > 0:
                    jsonfile[key] = value
            f.seek(0)
            json.dump(jsonfile, f, indent=2)
            f.truncate()
            # print("Configuration of the default parameters for 'bfconvert' is complete")
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('configured_ometiff')
        #sys.stdout.write('configured_ometiff\n') ### VERY IMPORTANT STEP
    elif prompt == 'configure_omezarr':
        # print(prompt)
        argsdict = args.__dict__
        # print(argsdict)
        with open(os.path.join(scriptpath,  '..', 'params', 'params.json.default'), 'r+') as f:
            jsonfile = json.load(f)
            for key in bf2rawParams:
                value = argsdict[key]
                try:
                    current = jsonfile[key]
                except:
                    current = "<bioformats2raw defaults>"
                # print(value)
                if value is None:
                    keyprompt = input('Please enter value for %s\n'
                                      '%s\n'
                                      'Click enter to set the parameter to the initial defaults\n'
                                      'Enter "skip" or "s" if you would like to keep the parameter´s current value, which is %s\n' % (key, bf2rawParams[key], current))
                    # print(keyprompt)
                    if keyprompt is None:
                        pass
                    else:
                        args.__dict__[key] = keyprompt
            for key, value in args.__dict__.items():
                if (value == 's') | (value == 'skip'):
                    pass
                elif len(value) == 0:
                    try:
                        del jsonfile[key]
                    except:
                        pass
                elif len(value) > 0:
                    jsonfile[key] = value
            f.seek(0)
            json.dump(jsonfile, f, indent=2)
            f.truncate()
        # print("Configuration of the default parameters for 'bioformats2raw' is complete")
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('configured_omezarr')
        #sys.stdout.write('configured_omezarr\n') ### VERY IMPORTANT STEP - BU STEPI DEGISTIRMEK LAZIM
    elif (prompt == 'ometiff') | (prompt == 'omezarr'):
        # print(keys)
        os.chdir(relpath)
        if args.in_path.startswith('/'):
            pass
        elif not args.in_path.startswith('/'):
            if args.source_type == 's3':
                pass
            elif args.source_type == 'bia':
                pass
            else:
                args.in_path = relpath + '/' + args.in_path
        ###
        if args.out_path.startswith('/'):
            pass
        elif not args.out_path.startswith('/'):
            if args.dest_type == 's3':
                pass
            elif args.dest_type == 'bia':
                pass
            else:
                args.out_path = os.path.realpath(args.out_path)
        os.chdir(scriptpath)
        #print(args)
        cmdroot = ["python", "./edit_params_file.py".format(scriptpath), "-f", '../params/params.json', "-df", '../params/params.json.default']
        cmd = []
        idx = 0
        # print(args)
        for key, value in args.__dict__.items():
            # print((key, value))
            if str(value) == str("None"):
                pass
            elif value is None:
                pass
            elif str(value) == str("False") and (key != "merge_files"):
                pass
            elif value is False and (key != "merge_files"):
                pass
            else:
                cmd.append(cmdroot + ["--key", key, "--value", "%s" % value])
            if prompt == 'ometiff':
                # print(key)
                if idx == 0:
                    cmd.append(cmdroot + ["--key", 'output_type', "--value", "ometiff"])
                    for bf2raw_key in bf2raw_params:
                        # print("bf2raw param: %s" % key)
                        cmd.append(cmdroot + ["--key", bf2raw_key, "--deletekey", "true"])
            elif prompt == 'omezarr':
                if idx == 0:
                    cmd.append(cmdroot + ["--key", 'output_type', "--value", "omezarr"])
                    for bftools_key in bftools_params:
                        # print("bftools param: %s" % key)
                        cmd.append(cmdroot + ["--key", bftools_key, "--deletekey", "true"])
            if all([(args.dest_type == "local"), (args.source_type == "local")]):  # if destination is local, don't even add the s3 parameters
                # print("locality param: %s" % key)
                if key.startswith('S3'):
                    cmd.append(cmdroot + ["--key", key, "--deletekey", "true"])
                elif key.startswith('BIA'):
                    cmd.append(cmdroot + ["--key", key, "--deletekey", "true"])
                else:
                    pass
            elif all([(args.dest_type != "s3"), (args.source_type != "s3")]):
                if key.startswith('S3'):
                    cmd.append(cmdroot + ["--key", key, "--deletekey", "true"])
                else:
                    pass
            elif all([(args.dest_type != "bia"), (args.source_type != "bia")]):
                if key.startswith('bia'):
                    cmd.append(cmdroot + ["--key", key, "--deletekey", "true"])
                else:
                    pass
            # cmd.append(cmdroot + ["--key", key, "--value", "%s" % value])
            # cmd.append(cmdroot + ["--key", key, "--value", "%s" % value])
            idx += 1
        if os.path.exists('../params/params.json'):
            os.remove('../params/params.json')
        for item in cmd:
            subprocess.run(item)
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('converted')
        #sys.stdout.write('converted') ### VERY IMPORTANT STEP
    elif (prompt == 'reset_defaults'):
        backup_params = os.path.join(scriptpath, '..', 'params', 'params.json.backup')
        default_params = os.path.join(scriptpath, '..', 'params', 'params.json.default')
        shutil.copy(backup_params, default_params)
        with open(os.path.join(scriptpath,  '.process'), 'w') as writer:
            writer.write('resetted')
