# BatchConvert

A command line tool for converting image data into either of the standard file formats OME-TIFF or OME-Zarr. 

The tool wraps the dedicated file converters bfconvert and bioformats2raw to convert into OME-TIFF or OME-Zarr,
respectively. The workflow management system Nextflow is used to perform conversion in parallel for batches of images. 

The tool also wraps s3 and Aspera clients (go-mc and aspera-cli, respectively). Therefore, input and output locations can 
be specified as local or remote storage and file transfer will be performed automatically. The conversion can be run on 
HPC with Slurm.  

## Installation & Dependencies

**Important** note: The package has been so far only tested on Ubuntu 20.04.

The minimal dependency to run the tool is NextFlow, which should be installed and made accessible from the command line.

If conda exists on your system, you can install BatchConvert together with NextFlow using the following script:
```
git clone https://github.com/Euro-BioImaging/BatchConvert.git && \ 
source BatchConvert/installation/install_with_nextflow.sh
```


If you already have NextFlow installed and accessible from the command line, or if you prefer to install it manually (e.g., as shown [here](https://www.nextflow.io/docs/latest/getstarted.html)), 
you can also install BatchConvert alone, using the following script:
```
git clone https://github.com/Euro-BioImaging/BatchConvert.git && \ 
source BatchConvert/installation/install.sh
```


Other dependencies (which will be **automatically** installed):
- bioformats2raw (entrypoint bioformats2raw)
- bftools (entrypoint bfconvert)
- go-mc (entrypoint mc)
- aspera-cli (entrypoint ascp)

These dependencies will be installed and cached automatically at the first execution of the conversion command. The mode of installation can be specified by using the 
command line option ``--profile`` or `-pf`. Depending on how this option is specified, the dependencies can be acquired via conda or docker/singularity containers. 

Specifying ``--profile conda`` (default) will install the dependencies to an 
environment at ``./.condaCache`` and use this environment to run the workflow. This option 
requires that miniconda/anaconda is installed on your system.    

Alternatively, specifying ``--profile docker`` or ``--profile singularity`` will pull a docker or 
singularity image with the dependencies, respectively, and use this image to run the workflow.
These options require that the respective container runtime (docker or singularity) is available on 
your system. If singularity is being used, a cache directory will be created at the path 
``./.singularityCache`` where the singularity image is stored. 

Finally, you can still choose to install the dependencies manually and use your own installations to run
the workflow. In this case, you should specify ``--profile standard`` and make sure the entrypoints
specified above are recognised by your shell.  

## Examples

### Local conversion
Convert a batch of images on your local storage into OME-TIFF format. Note that the `input_path`
in the command given below is typically a directory with multiple image files but a single image file
can also be passed:\
`batchconvert ometiff -pf conda <input_path> <output_path>`

As conda is the default profile, (specified in the file `params/params.json.default`), it does not have to be 
explicitly included in the command line. Thus the command can be shortened to:\
`batchconvert ometiff <input_path> <output_path>`

Convert only the first channel of the images:\
`batchconvert ometiff -chn 0 <input_path> <output_path>`

Crop the images being converted along x and y axis by 150 pixels:\
`batchconvert ometiff -cr 0,0,150,150 <input_path> <output_path>`

Convert into OME-Zarr instead:\
`batchconvert omezarr <input_path> <output_path>`

Convert into OME-Zarr with 3 resolution levels:\
`batchconvert omezarr -rz 3 <input_path> <output_path>`

Select a subset of images with a matching string such as "mutation":\
`batchconvert omezarr -p mutation <input_path> <output_path>`

Select a subset of images using wildcards. Note that the use of "" around 
the input path is necessary with wildcards:\
`batchconvert omezarr "<input_path>/*D3*.oir" <output_path>`

Convert by using a singularity container instead of conda environment (requires
singularity to be installed on your system):\
`batchconvert omezarr -pf singularity "<input_path>/*D3*.oir" <output_path>`

Convert by using a docker container instead of conda environment (requires docker
to be installed on your system):\
`batchconvert omezarr -pf docker "<input_path>/*D3*.oir" <output_path>`

Convert and upload the output to an s3 bucket. Note that the output path is 
created relative to the bucket specified in your s3 parameters:\
`batchconvert omezarr -dt s3 <input_path> <output_path>`

Receive an input from an s3 bucket, convert locally and upload to the same bucket.
Note that wildcards cannot be used when the input is from s3. Use pattern matching
option `-p` for selecting a subset:\
`batchconvert omezarr -p mutation -st s3 -dt s3 <input_path> <output_path>`

### Conversion on slurm

The examples given above can also be run on slurm by specifying `-pf cluster` option. 
Note that this option automatically uses singularity container:\
`batchconvert omezarr -pf cluster -p .oir <input_path> <output_path>`







