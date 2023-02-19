#!/usr/bin/env bash

cat $HOME/.bashrc | grep -v BatchConvert > $HOME/bashrc_replace;
cat $HOME/bashrc_replace > $HOME/.bashrc;

export PATH=`echo $PATH | tr ":" "\n" | grep -v "BatchConvert" | tr "\n" ":"`;

rm -rf $HOME/bashrc_replace;
source $HOME/.bashrc;
