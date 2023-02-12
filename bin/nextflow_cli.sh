#!/usr/bin/env bash
SCRIPTPATH=$( dirname -- ${BASH_SOURCE[0]}; );
nextflow -C $SCRIPTPATH/../configs/bftools.config run $SCRIPTPATH/../pff2ometiff.nf -params-file $SCRIPTPATH/../params/params.json -profile conda