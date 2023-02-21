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
cd $SCRIPTPATH;

conda create --yes --name nflow python=3.9 && \
conda install --yes -n nflow -c bioconda nextflow=22.10.0-0 && \
echo "conda run -n nflow nextflow \$@" > nextflow && \
chmod 777 nextflow
cd -
