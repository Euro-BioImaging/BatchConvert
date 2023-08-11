#!/usr/bin/env bash
SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );
nextflow -C $SCRIPTPATH/../configs/bftools.config -log $SCRIPTPATH/../WorkDir/logs/.nextflow.log run $SCRIPTPATH/../pff2omezarr.nf -params-file $SCRIPTPATH/../params/params.json -profile conda;
nextflow clean but none -n -f;