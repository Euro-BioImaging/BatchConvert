#!/usr/bin/env bash

# make SCRIPTPATH an environment variable TODO
SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );

set -f && \
pythonexe $SCRIPTPATH/bin/parameterise_conversion.py "$@";

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    process=$(cat $SCRIPTPATH/bin/.process)
  else
    printf "The batchonvert command seems to be invalid. Please try again. \n"
fi

if [[ $process == 'configured_s3' ]];
  then
    printf "Configuration of the default s3 credentials is complete\n";
elif [[ $process == 'configured_bia' ]];
  then
    printf "Configuration of the default bia credentials is complete\n";
elif [[ $process == 'configured_slurm' ]];
  then
    printf "Configuration of the default slurm parameters is complete\n";
elif [[ $process == 'configured_ometiff' ]];
  then
    printf "Configuration of the default parameters for 'bfconvert' is complete\n";
elif [[ $process == 'configured_omezarr' ]];
  then
    printf "Configuration of the default parameters for 'bioformats2raw' is complete\n";
elif [[ $process == 'resetted' ]];
  then
    printf "Default parameters were resetted.\n";
elif [[ $process == 'converted' ]];
  then
    cd $SCRIPTPATH/bin && \

    pythonexe construct_cli.py > batchconvert_cli.sh && \
    pythonexe construct_nextflow_cli.py > nextflow_cli.sh && \
    printf "Nextflow script has been created. Workflow is beginning.\n"
    cd - && \

    $SCRIPTPATH/bin/nextflow_cli.sh
fi

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    rm $SCRIPTPATH/bin/.process
fi

rm -rf $SCRIPTPATH/WorkDir/work &> /dev/null;
rm -rf /scratch/.batchconvert/work &> /dev/null;
rm -rf $SCRIPTPATH/WorkDir/logs &> /dev/null;
rm -rf /scratch/.batchconvert/logs &> /dev/null;

pythonexe $SCRIPTPATH/bin/cleanup.py &> /dev/null


# this runs the nextflow workflow which will consume the updated command line in the bin:

# sudo rm -r work


