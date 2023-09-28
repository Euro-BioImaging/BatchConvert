#!/usr/bin/env bash

# TODO make SCRIPTPATH an environment variable

SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );
source $SCRIPTPATH/bin/utils.sh

set -f && \
pythonexe $SCRIPTPATH/bin/parameterise_conversion.py "$@";

if [[ -f $SCRIPTPATH/bin/.stderr ]];
  then
    error=$(cat $SCRIPTPATH/bin/.stderr);
    rm $SCRIPTPATH/bin/.stderr;
fi;

if [[ ${#error} > 0 ]];
  then
    printf "${RED}$error${NORMAL}\n"
    printf "${RED}The batchonvert command is invalid. Please try again.${NORMAL}\n"
    exit
fi

if [[ -f $SCRIPTPATH/bin/.stdout ]];
  then
    result=$(cat $SCRIPTPATH/bin/.stdout);
    rm $SCRIPTPATH/bin/.stdout;
fi;

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    process=$(cat $SCRIPTPATH/bin/.process)
  else
    printf "${RED}The batchonvert command is invalid. Please try again.${NORMAL}\n"
fi

if [[ $result == "inputpatherror" ]];
  then
    printf "${RED}Error: The input path does not exist.\n${NORMAL}"
    exit
elif [[ ${#result} > 0 ]];
  then
    if [[ $process == 'parameters_shown' ]];
      then
        printf "${NORMAL}$result${NORMAL}\n"
      else
        printf "${RED}$result${NORMAL}\n"
        exit
    fi
fi

if [[ -f $SCRIPTPATH/bin/.afterrun ]];
  then
    afterrun=$(cat $SCRIPTPATH/bin/.afterrun)
  else
    afterrun="nan"
fi

if [[ $process == 'configured_s3' ]];
  then
    printf "${GREEN}Configuration of the default s3 credentials is complete${NORMAL}\n";
elif [[ $process == 'configured_bia' ]];
  then
    printf "${GREEN}Configuration of the default bia credentials is complete${NORMAL}\n";
elif [[ $process == 'configured_slurm' ]];
  then
    printf "${GREEN}Configuration of the default slurm parameters is complete\n${NORMAL}";
elif [[ $process == 'configured_ometiff' ]];
  then
    printf "${GREEN}Configuration of the default parameters for 'bfconvert' is complete\n${NORMAL}";
elif [[ $process == 'configured_omezarr' ]];
  then
    printf "${GREEN}Configuration of the default parameters for 'bioformats2raw' is complete\n${NORMAL}";
elif [[ $process == 'configured_from_json' ]];
  then
    printf "${GREEN}Default parameters have been updated from a json file.\n${NORMAL}";
elif [[ $process == 'resetted' ]];
  then
    printf "${GREEN}Default parameters have been resetted.\n${NORMAL}";
elif [[ $process == 'parameters_shown' ]];
  then
    printf "${GREEN}Current default parameters displayed.\n${NORMAL}";
elif [[ $process == 'parameters_exported' ]];
  then
    printf "${GREEN}Current default parameters successfully exported.\n${NORMAL}";
elif [[ $process == "default_param_set" ]];
  then
    printf "${GREEN}Default parameter updated.\n${NORMAL}";
elif [[ $process == 'converted' ]];
  then
    cd $SCRIPTPATH/bin && \

    pythonexe construct_cli.py > batchconvert_cli.sh && \
    pythonexe construct_nextflow_cli.py > nextflow_cli.sh && \
    printf "${GREEN}Nextflow script has been created. Workflow is beginning.\n${NORMAL}"
    cd - && \

    $SCRIPTPATH/bin/nextflow_cli.sh
fi

if [[ -f $SCRIPTPATH/bin/.process ]];
  then
    rm $SCRIPTPATH/bin/.process
fi

if [[ $1 == "ometiff" ]] || [[ $1 == "omezarr" ]];
  then
    if [[ $afterrun != "noclean" ]];
      then
        # echo $afterrun
        pythonexe $SCRIPTPATH/bin/clean_workdir.py;
    fi
fi

if [[ -f $SCRIPTPATH/bin/.afterrun ]];
  then
  rm $SCRIPTPATH/bin/.afterrun
fi

pythonexe $SCRIPTPATH/bin/cleanup.py &> /dev/null



# this runs the nextflow workflow which will consume the updated command line in the bin:





