#!/usr/bin/env bash

# Ileride scriptpath ROOT adi altinda environment variable yapilacak
SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );

set -f && \
#python $SCRIPTPATH/bin/parameterise_conversion.py $@;
python $SCRIPTPATH/bin/parameterise_conversion.py "$@";

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    process=$(cat $SCRIPTPATH/bin/.process)
  else
    printf "The batchonvert command seems to be invalid. Please try again. \n"
fi

if [[ $process == 'configured_s3' ]];
  then
    printf "Configuration of default s3 credentials is complete\n";
elif [[ $process == 'configured_bia' ]];
  then
    printf "Configuration of default bia credentials is complete\n";
elif [[ $process == 'configured_slurm' ]];
  then
    printf "Configuration of default slurm credentials is complete\n";
elif [[ $process == 'configured_ometiff' ]];
  then
    printf "Configuration of the default parameters for 'bfconvert' is complete\n";
elif [[ $process == 'configured_omezarr' ]];
  then
    printf "Configuration of the default parameters for 'bioformats2raw' is complete\n";
elif [[ $process == 'converted' ]];
  then
    cd $SCRIPTPATH/bin && \

    python construct_cli.py > batchconvert_cli.sh && \
    python construct_nextflow_cli.py > nextflow_cli.sh && \
    printf "Nextflow script has been created. Workflow is beginning.\n"
    cd - && \

    $SCRIPTPATH/bin/nextflow_cli.sh
fi

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    rm $SCRIPTPATH/bin/.process
fi
# this runs the nextflow workflow which will consume the updated command line in the bin:

# sudo rm -r work


