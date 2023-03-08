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


If you already have NextFlow installed and accessible from the command line (or if you prefer to install it manually 
e.g., as shown [here](https://www.nextflow.io/docs/latest/getstarted.html)), you can also install BatchConvert alone, using the following script:
```
git clone https://github.com/Euro-BioImaging/BatchConvert.git && \ 
source BatchConvert/installation/install.sh
```


Other dependencies (which will be **automatically** installed):
- bioformats2raw (entrypoint bioformats2raw)
- bftools (entrypoint bfconvert)
- go-mc (entrypoint mc)
- aspera-cli (entrypoint ascp)

These dependencies will be pulled and cached automatically at the first execution of the conversion command. 
The mode of dependency management can  be specified by using the command line option ``--profile`` or `-pf`. Depending 
on how this option is specified, the dependencies will be acquired / run either via conda or via docker/singularity containers. 

Specifying ``--profile conda`` (default) will install the dependencies to an 
environment at ``./.condaCache`` and use this environment to run the workflow. This option 
requires that miniconda/anaconda is installed on your system.    

Alternatively, specifying ``--profile docker`` or ``--profile singularity`` will pull a docker or 
singularity image with the dependencies, respectively, and use this image to run the workflow.
These options assume that the respective container runtime (docker or singularity) is available on 
your system. If singularity is being used, a cache directory will be created at the path 
``./.singularityCache`` where the singularity image is stored. 

Finally, you can still choose to install the dependencies manually and use your own installations to run
the workflow. In this case, you should specify ``--profile standard`` and make sure the entrypoints
specified above are recognised by your shell.  


## Configuration

BatchConvert can be configured to have default options for file conversion and transfer. Probably, the most important sets of parameters
to be configured include credentials for the remote ends. The easiest way to configure remote locations is by running the interactive 
configuration command as indicated below.

### Configuration of the s3 object store

Run the interactive configuration command: 

`batchconvert configure_s3_remote`

This will start a sequence of requests for s3 credentials such as name, url, access, etc. Provide each requested credential and click
enter. Continue this cycle until the process is finished. The terminal should roughly look like this:

```
oezdemir@pc-ellenberg108:~$ batchconvert configure_s3_remote
enter remote name (for example s3)
s3
enter url:
https://s3.embl.de
enter access key:
<your-access-key>
enter secret key:
<your-secret-key>
enter bucket name:
<your-bucket>
Configuration of default s3 credentials is complete
```


### Configuration of the BioStudies user space

Run the interactive configuration command: 

`batchconvert configure_bia_remote`

This will prompt a request for the secret directory to connect to. Enter the secret directory for your user space and click enter. The terminal
should roughly look like this:

```
oezdemir@pc-ellenberg108:~$ batchconvert configure_bia_remote
enter the secret directory for BioImage Archive user space:
<your-secret-directory>
Configuration of default bia credentials is complete
```


## Examples

### Local conversion

#### Parallel conversion of files to separate OME-TIFFs / OME-Zarrs:
Convert a batch of images on your local storage into OME-TIFF format. 
Note that the `input_path` in the command given below is typically a 
directory with multiple image files but a single image file can also be passed:\
`batchconvert ometiff -pf conda <input_path> <output_path>` \

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
the input path is necessary when using wildcards:\
`batchconvert omezarr "<input_path>/*D3*.oir" <output_path>`

Convert by using a singularity container instead of conda environment (requires
singularity to be installed on your system):\
`batchconvert omezarr -pf singularity "<input_path>/*D3*.oir" <output_path>`

Convert by using a docker container instead of conda environment (requires docker
to be installed on your system):\
`batchconvert omezarr -pf docker "<input_path>/*D3*.oir" <output_path>`

Convert local data and upload the output to an s3 bucket. Note that the output 
path is created relative to the bucket specified in your s3 parameters:\
`batchconvert omezarr -dt s3 <input_path> <output_path>`

Receive input files from an s3 bucket, convert locally and upload the output to 
the same bucket. Note that wildcards cannot be used when the input is from s3. 
Use pattern matching option `-p` for selecting a subset of input files:\
`batchconvert omezarr -p mutation -st s3 -dt s3 <input_path> <output_path>`

Receive input files from your private BioStudies user space and convert them locally.
Use pattern matching option `-p` for selecting a subset of input files:\
`batchconvert omezarr -p mutation -st bia <input_path> <output_path>`

Receive an input from an s3 bucket, convert locally and upload the output to your 
private BioStudies user space. Use pattern matching option `-p` for selecting a subset 
of input files:\
`batchconvert omezarr -p mutation -st s3 -dt bia <input_path> <output_path>`


Note that in all the examples shown above, BatchConvert treats each input file as separate,
standalone data point, disregarding the possibility that some of the input files might belong to 
the same multidimensional array. Thus, each input file is converted to an independent 
OME-TIFF / OME-Zarr and the number of outputs will thus equal the number of selected input files.
An alternative scenario is discussed below.

#### Parallel conversion of file groups by stacking multiple files into single OME-TIFFs / OME-Zarrs:

When the flag `--merge_files` is specified, BatchConvert tries to find out which input files might 
belong to the same multidimensional array based on the patterns in the filenames. Then a "grouped conversion" 
is performed, meaning that the files belonging to the same dataset will be converted together into 
a single OME-TIFF / OME-Zarr stack, in that files will be concatenated along specific dimension(s) 
during the conversion. Multiple file groups in the input directory can thus be detected and converted 
in parallel. 

This feature uses Bio-Formats's pattern files as described [here](https://docs.openmicroscopy.org/bio-formats/6.6.0/formats/pattern-file.html).
However, BatchConvert generates pattern files automatically, allowing the user to directly use the 
input directory in the conversion command. BatchConvert also has the option of specifying the 
concatenation axes in the command line, which is especially useful in cases where the file names 
do not contain dimension information.  

To be able to use the `--merge files` flag, the input file names must obey certain rules:
1. File names in the same group must be consistent, except for one or more **"variable field(s)"**. 
2. The variable field(s) must be numeric and incremental within a group.
3. The length of variable fields must be uniform within the group. For instance, if the
variable field has values reaching multi-digit numbers, leading "0"s should be included where needed 
in the file names to make the variable field length uniform within the group.
4. Typically, each variable field should follow a dimension specifier. What patterns can be used as 
dimension specifiers are explained [here](https://docs.openmicroscopy.org/bio-formats/6.6.0/formats/pattern-file.html).
However, BatchConvert also has the option `--concatenation_order`, which allows the user to
specify from the command line, the dimension(s), along which the files must be concatenated.
5. File names that are unique and cannot be associated with any group will be excluded from 
grouped conversion. In other words, BatchConvert assumes a group must consist of 2 or more files. 

Below are some examples of grouped conversion commands, together with acceptable and unacceptable
filenames:

**Example 1:**
```
time-series/test_img_T2
time-series/test_img_T4
time-series/test_img_T6
time-series/test_img_T8
time-series/test_img_T10
time-series/test_img_T12
```
In this example, leading zeroes are missing in the variable field in some of the file names. 
Here is the corrected version for the above example:
```
time-series/test_img_T02
time-series/test_img_T04
time-series/test_img_T06
time-series/test_img_T08
time-series/test_img_T10
time-series/test_img_T12
```
Convert this folder to a single OME-TIFF: \
`batchconvert --ometiff --merge_files <input_path>/time-series <output_path>`

**Example 2**: 
```
test_img_T2
test_img_T4
test_img_T5
test_img_T7
```
In this example, the increments in the variable field are non-uniform. BatchConvert does not 
accept this fileset as a valid group.

**Example 3**
```
multichannel_time-series/test_img_C1-T1
multichannel_time-series/test_img_C1-T2
multichannel_time-series/test_img_C1-T3
multichannel_time-series/test_img_C2-T1
multichannel_time-series/test_img_C2-T2
```
In this example the channel-2 does not have the same number of timeframes as channel-1. 
BatchConvert will also reject this fileset as a valid group. The corrected version should 
look like:
```
multichannel_time-series/test_img_C1-T1
multichannel_time-series/test_img_C1-T2
multichannel_time-series/test_img_C1-T3
multichannel_time-series/test_img_C2-T1
multichannel_time-series/test_img_C2-T2
multichannel_time-series/test_img_C2-T3
```

Convert this folder to a single OME-Zarr: \
`batchconvert --omezarr --merge_files <input_path>/multichannel_time-series <output_path>`

**Example 4**
```
folder_with_multiple_groups/test_img_C1-T1
folder_with_multiple_groups/test_img_C1-T2
folder_with_multiple_groups/test_img_C2-T1
folder_with_multiple_groups/test_img_C2-T2
folder_with_multiple_groups/test_img_T1-Z1
folder_with_multiple_groups/test_img_T1-Z2
folder_with_multiple_groups/test_img_T1-Z3
folder_with_multiple_groups/test_img_T2-Z1
folder_with_multiple_groups/test_img_T2-Z2
folder_with_multiple_groups/test_img_T2-Z3
```

This is an example of a case, where there are multiple filename patterns in the input folder. 
BatchConvert will detect the two patterns in this folder and perform two grouped conversions. 
The output folders will be named as `test_img_CRange{1-2-1}-TRange{1-2-1}.ome.zarr` and 
`test_img_TRange{1-2-1}-ZRange{1-3-1}.ome.zarr`. 

Convert this folder: \
`batchconvert --omezarr --merge_files <input_path>/folder_with_multiple_groups <output_path>`

**Example 5**
```
folder_with_multiple_groups/test_img_1-1
folder_with_multiple_groups/test_img_1-2
folder_with_multiple_groups/test_img_2-1
folder_with_multiple_groups/test_img_2-2
folder_with_multiple_groups/test_img_T1-Z1
folder_with_multiple_groups/test_img_T1-Z2
folder_with_multiple_groups/test_img_T1-Z3
folder_with_multiple_groups/test_img_T2-Z1
folder_with_multiple_groups/test_img_T2-Z2
folder_with_multiple_groups/test_img_T2-Z3
```

This example uses the same filesets as in the example 4, except that the file names in
the first group lack any dimension specifier. In such a possible scenario, BatchConvert 
allows the user to specify the concatenation axes via `--concatenation_order` option. This
option expects comma-separated strings of dimensions for each group. In this example, 
the user must provide a string of 2 characters, such as `ct` for channel and time, for group 1, 
since there are two variable fields for this group. Since group 2 already has dimension specifiers,
the user does not need to specify anything for this group, and can enter `auto` for automatic
detection of the specifiers. 

So the following line can be used to convert this folder: \
`batchconvert --omezarr --merge_files --concatenation_order ct,auto <input_path>/folder_with_multiple_groups <output_path>`

Note that `--concatenation_order` will override any existing dimension specifiers.

### Conversion on slurm

All the examples given above can also be run on slurm by specifying `-pf cluster` option. 
Note that this option automatically uses singularity profile:\
`batchconvert omezarr -pf cluster -p .oir <input_path> <output_path>`







