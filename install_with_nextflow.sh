#!/usr/bin/env bash

rel_SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );

# https://stackoverflow.com/questions/3915040/how-to-obtain-the-absolute-path-of-a-file-via-shell-bash-zsh-sh
function abspath() {
    # generate absolute path from relative path
    # $1     : relative filename
    # return : absolute path
    if [ -d "$1" ]; then
        # dir
        (cd "$1"; pwd)
    elif [ -f "$1" ]; then
        # file
        if [[ $1 = /* ]]; then
            echo "$1"
        elif [[ $1 == */* ]]; then
            echo "$(cd "${1%/*}"; pwd)/${1##*/}"
        else
            echo "$(pwd)/$1"
        fi
    fi
}

SCRIPTPATH=$(abspath $rel_SCRIPTPATH);

chmod -R 777 $SCRIPTPATH;


### Install nextflow and add it to the path

cd $SCRIPTPATH;

conda create --yes --name nflow python=3.9 && \
conda install --yes -n nflow -c bioconda nextflow=22.10.0-0 && \
mv nextflow.sample nextflow
cd -

### Make sure the correct python is used in the batchconvert script

v_info=$( python --version )
VP=${v_info:7:1}

if [[ $VP == 3 ]];
  then
    printf "The following python will be used to execute python commands in batchconvert script: $( which python ) \n"
    if ! [ -f $SCRIPTPATH/pythonexe ];then
	ln -s $( which python ) $SCRIPTPATH/pythonexe;
    fi
elif ! [[ $VP == 3 ]];
  then
    printf "Python command refers to the following python: $( which python ), which cannot be used in the batchconvert script \nWill search the system for python3 \n";
    if command -v python3 &> /dev/null;
      then
	printf "python3 was found at $( which python3 ) \n";
	printf "This python will be used in the batchconvert script \n "
        if ! [ -f $SCRIPTPATH/pythonexe ];then
	   ln -s $( which python3 ) $SCRIPTPATH/pythonexe;
        fi
        printf "$(pythonexe --version) \n"
      else
        printf "Looks like python 3 does not exist on your system. Please install python3 and reinstall BatchConvert. \n"
        exit
    fi
fi

### Add BatchConvert directory to the PATH.

if ! echo $PATH | tr ":" "\n" | grep "BatchConvert" &> /dev/null;
then
	echo "export PATH="$SCRIPTPATH:$PATH"" >> $HOME/.bashrc;
fi;

source $HOME/.bashrc;

