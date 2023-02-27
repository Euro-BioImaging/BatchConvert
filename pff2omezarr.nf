#!/usr/bin/env nfprojects
nextflow.enable.dsl=2
// nextflow.enable.moduleBinaries = true

include { Convert_Concatenate2SingleOMEZARR; Convert_EachFile2SeparateOMEZARR; Transfer_Local2S3Storage; Transfer_S3Storage2Local; Transfer_Local2PrivateBiostudies; Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local } from "./modules/modules.nf"

// TODO: add an optional remove-workdir parameter and a remove-workdir script to the end of the workflow (in Groovy)

workflow {
    // If the input dataset is in s3, bring it to the execution environment first:
    // Note that this scenario assumes that the input path corresponds to a directory at s3 (not a single file)
    if ( params.source_type == "s3" ) {
        ch0 = Channel.of(params.in_path)
        Transfer_S3Storage2Local(ch0)
        ch1 = Transfer_S3Storage2Local.out.map { file(it).listFiles() }.flatten()
        ch = ch1.filter { it.toString().contains(params.pattern) }
    }
    else if ( params.source_type == "bia" ) {
        ch0 = Channel.of(params.in_path)
        Transfer_PrivateBiostudies2Local(ch0)
        ch1 = Transfer_PrivateBiostudies2Local.out.map { file(it).listFiles() }.flatten()
        ch2 = ch1.map { file(it).listFiles() }.flatten()
        ch = ch2.filter { it.toString().contains(params.pattern) }
    }
//    else if ( params.source_type == "public_bia" ) {
//        ch0 = Channel.of(params.in_path)
//        Transfer_PublicBiostudies2Local(ch0)
//        ch1 = Transfer_PublicBiostudies2Local.out.map { file(it).listFiles() }.flatten()
//        ch2 = ch1.map { file(it).listFiles() }.flatten()
//        ch = ch2.filter { it.toString().contains(params.pattern) }
//    }
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
    if ( params.source_type == "local" ) {
        if ( params.merge_files == "True" ) {
            output = Convert_Concatenate2SingleOMEZARR(params.in_path)
        }
        else {
            output = Convert_EachFile2SeparateOMEZARR(ch)
        }
    }
    else if ( params.source_type == "s3" ) {
        if ( params.merge_files == "True" ) {
            output = Convert_Concatenate2SingleOMEZARR(Transfer_S3Storage2Local.out)
        }
        else {
            output = Convert_EachFile2SeparateOMEZARR(ch)
        }
    }
    else if ( params.source_type == "bia" ) {
        if ( params.merge_files == "True" ) {
            output = Convert_Concatenate2SingleOMEZARR(Transfer_PrivateBiostudies2Local.out)
        }
        else {
            output = Convert_EachFile2SeparateOMEZARR(ch)
        }
    }
    if ( params.dest_type == "s3" ) {
        // Note that if the dest_type is s3, the output must be uploaded to the s3 bucket.
        // If dest_type is local, no need to do anything. module will do the publishDir.
        Transfer_Local2S3Storage(output)
    }
    if ( params.dest_type == "bia" ) {
        // Note that if the dest_type is bia, the output must be uploaded to the bia bucket.
        // If dest_type is local, no need to do anything. module will do the publishDir.
        Transfer_Local2PrivateBiostudies(output)
    }
}