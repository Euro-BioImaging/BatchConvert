#!/usr/bin/env bash
SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );
nextflow -C $SCRIPTPATH/../configs/bftools.config -log /home/oezdemir/PycharmProjects/nfprojects/BatchConvert/nfWorkDir/logs/.nextflow.log run $SCRIPTPATH/../pff2omezarr.nf -params-file $SCRIPTPATH/../params/params.json -profile docker;
nextflow clean but none -n -f;