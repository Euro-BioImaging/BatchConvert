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

#mkdir -p $HOME/.batchconvert/bin;
#chmod -R 777 $HOME/.batchconvert;
chmod -R 777 $SCRIPTPATH;

#echo $(ls $SCRIPTPATH);

#echo $'#!/usr/bin/env bash' > $HOME/.batchconvert/bin/batchconvert && \
#echo "$SCRIPTPATH/batchconvert.sh \$@" >> $HOME/.batchconvert/bin/batchconvert && \
#chmod 777 $HOME/.batchconvert/bin/batchconvert;

#cat $HOME/.batchconvert/bin/batchconvert;

if ! echo $PATH | tr ":" "\n" | grep "batchconvert" &> /dev/null;
then
	echo "export PATH="$SCRIPTPATH:$PATH"" >> $HOME/.bashrc;
fi;

source $HOME/.bashrc;
