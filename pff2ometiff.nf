#!/usr/bin/env nfprojects
nextflow.enable.dsl=2
// nextflow.enable.moduleBinaries = true

include { bfconvert; mirror2s3; mirror2local; mirror2bia; mirror_bia2local; stageLocal } from "./modules/modules.nf"

// TODO: add an optional remove-workdir parameter and a remove-workdir script to the end of the workflow (in Groovy)

workflow {
    // If the input dataset is in s3, bring it to the execution environment first:
    // Note that this scenario assumes that the input path corresponds to a directory at s3 (not a single file)
    if ( params.source_type == "s3" ) {
        ch0 = Channel.of(params.in_path)
        mirror2local(ch0)
        ch1 = mirror2local.out.map { file(it).listFiles() }.flatten()
        ch = ch1.filter { it.toString().contains(params.pattern) }
    }
    else if ( params.source_type == "bia" ) {
        ch0 = Channel.of(params.in_path)
        mirror_bia2local(ch0)
        ch1 = mirror_bia2local.out.map { file(it).listFiles() }.flatten()
        ch2 = ch1.map { file(it).listFiles() }.flatten()
        ch = ch2.filter { it.toString().contains(params.pattern) }
    }
    else if ( params.source_type == "local" ) {
        def fpath = file(params.in_path)
        // Note the above assignment yields either a list of files (with globbing), a single file (if the parameter in_path corresponds to a file path) a directory (if the parameter in_path corresponds to a directory path)
        // Make sure a proper channel is created in any of these cases:
        if  ( fpath instanceof List ){
            ch = Channel.fromPath(params.in_path).filter { it.toString().contains(params.pattern) }
        }
        else if ( fpath.isDirectory() ) {
            ch0 = Channel.of(fpath.listFiles()).flatten()
            ch = ch0.filter { it.toString().contains(params.pattern) }
        }
        else if ( fpath.isFile() ) {
            println fpath
            ch0 = Channel.of(fpath).flatten()
            ch = ch0.filter { it.toString().contains(params.pattern) }
        }
    }
    //Once the channel is created, run the conversion. Conversion is either kept local or transferred to s3 depending on the dest parameter.
    if ( params.dest_type == "local" ) {
        bfconvert(ch)
    }
    else if ( params.dest_type == "s3" ) {
        bfconvert(ch)
        mirror2s3(bfconvert.out)
    }
    else if ( params.dest_type == "bia" ) {
        bfconvert(ch)
        mirror2bia(bfconvert.out)
    }
    // TODO: add remove-workdir here.
}
