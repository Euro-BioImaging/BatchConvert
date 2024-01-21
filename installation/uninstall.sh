#!/usr/bin/env bash

rel_SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );
source $rel_SCRIPTPATH/../bin/utils.sh

SCRIPTPATH=$(abspath $rel_SCRIPTPATH)/..;
chmod -R 777 $SCRIPTPATH;


cat $HOME/.bashrc | grep -v BatchConvert > $HOME/bashrc_replace;
cat $HOME/bashrc_replace > $HOME/.bashrc;

export PATH=`echo $PATH | tr ":" "\n" | grep -v "BatchConvert" | tr "\n" ":"`;

rm -rf $HOME/bashrc_replace;
source $HOME/.bashrc;

cd $SCRIPTPATH/..
rm -rf BatchConvert
cd -

