#!/usr/bin/env bash

cat $HOME/.bashrc | grep -v BatchConvert > $HOME/bashrc_replace;

cat $HOME/bashrc_replace > $HOME/.bashrc;

rm -rf $HOME/bashrc_replace;

source $HOME/.bashrc;

