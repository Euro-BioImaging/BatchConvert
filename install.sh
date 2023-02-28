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


### Make sure that python3 is being used in the batchconvert script.

SCRIPTPATH=$(abspath $rel_SCRIPTPATH);
#printf SCRIPTPATH
chmod -R 777 $SCRIPTPATH;

v_info=$( python --version )
VP=${v_info:7:1}

if [[ $VP == 3 ]];
  then
    printf "Python 3 exists and will be used for executing the python commands in the batchconvert script."
    ln -s $( which python ) $SCRIPTPATH/pythonexe
elif ! [[ $v_python == 3 ]];
  then
    if command -v python3 &> /dev/null;
      then
        if ! [ -f $SCRIPTPATH/pythonexe ];then
          ln -s $( which python3 ) $SCRIPTPATH/pythonexe;
        fi
        printf "$(pythonexe --version) \n"
      else
        printf "Looks like python 3 does not exist on your system. BatchConvert expects python 3."
        exit
    fi
fi

### Add BatchConvert directory to the PATH.

if ! echo $PATH | tr ":" "\n" | grep "BatchConvert" &> /dev/null;
then
	echo "export PATH="$SCRIPTPATH:$PATH"" >> $HOME/.bashrc;
fi;

source $HOME/.bashrc;


