#!/usr/bin/env nfprojects
nextflow.enable.dsl=2
// nextflow.enable.moduleBinaries = true

include { createPatternFile1; createPatternFile2; Convert_Concatenate2SingleOMETIFF; Convert_EachFile2SeparateOMETIFF; Transfer_Local2S3Storage; Transfer_S3Storage2Local; Transfer_Local2PrivateBiostudies; Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local } from "./modules/modules.nf"
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList } from "./modules/modules.nf"

// TODO: add an optional remove-workdir parameter and a remove-workdir script to the end of the workflow (in Groovy)

workflow {
    // If the input dataset is in s3 or bia, bring it to the execution environment first:
    // Note that this scenario assumes that the input path corresponds to a directory at s3 (not a single file)
    if ( params.source_type == "s3" ) {
        ch0 = Channel.of(params.in_path)
        Transfer_S3Storage2Local(ch0)
        ch1 = Transfer_S3Storage2Local.out.map { file(it).listFiles() }.flatten()
        ch2 = ch1.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch2.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        else {
            ch = ch2
        }
    }
    else if ( params.source_type == "bia" ) {
        ch0 = Channel.of(params.in_path)
        Transfer_PrivateBiostudies2Local(ch0)
        ch1 = Transfer_PrivateBiostudies2Local.out.map { file(it).listFiles() }.flatten()
        ch2 = ch1.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch2.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        else {
            ch = ch2
        }
    }
    else if ( params.source_type == "local" ) {
        // Create a branch leading either to a grouped conversion or one-to-one conversion.
        if ( params.merge_files == "True" ) {
            ch = "NULL"
        }
        else {
            def fpath = file(params.in_path)
            // Note the above assignment yields either a list of files (with globbing), a single file (if the parameter in_path corresponds to a file path) a directory (if the parameter in_path corresponds to a directory path)
            // Make sure a proper channel is created in any of these 3 cases:
            if  ( fpath instanceof List ){
                ch1 = Channel.fromPath(params.in_path).filter { it.toString().contains(params.pattern) }
            }
            else if ( fpath.isDirectory() ) {
                ch0 = Channel.of(fpath.listFiles()).flatten()
                ch1 = ch0.filter { it.toString().contains(params.pattern) }
            }
            else if ( fpath.isFile() ) {
                ch0 = Channel.of(fpath).flatten()
                ch1 = ch0.filter { it.toString().contains(params.pattern) }
            }
            // ch1 must be acquired by this point based on the 3 cases above, now apply reject_pattern filter
            if ( params.reject_pattern.size() > 0 ) {
                ch = ch1.filter { !(it.toString().contains(params.reject_pattern)) }
            }
            else {
                ch = ch1
            }
        }
    }
    //Here check if the concatenation order is to be automatically inferred or not
    //Once the channel is created, run the conversion. Conversion is either kept local or transferred to s3 depending on the dest parameter.
    if ( params.source_type == "local" ) {
        // Create a branch leading either to a grouped conversion or one-to-one conversion.
        if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            is_correctNames = verify_filenames_fromPath(params.in_path, params.pattern, params.reject_pattern)
            if ( is_auto && is_correctNames ) {
                pattern_files = createPatternFile1(params.in_path).flatten()
            }
            else {
                pattern_files = createPatternFile2(params.in_path).flatten()
            }
            ch = pattern_files.filter { it.toString().contains(".pattern") }
            output = Convert_Concatenate2SingleOMETIFF(ch, params.in_path)
        }
        else {
            output = Convert_EachFile2SeparateOMETIFF(ch)
        }
    }
    else if ( params.source_type == "s3" ) {
        // Create a branch leading either to a grouped conversion or one-to-one conversion.
        if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            chlist = Transfer_S3Storage2Local.out.collect()
            is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
            if ( is_auto && is_correctNames ) {
                pattern_files = createPatternFile1(Transfer_S3Storage2Local.out).flatten()
            }
            else {
                pattern_files = createPatternFile2(Transfer_S3Storage2Local.out).flatten()
            }
            ch = pattern_files.filter { it.toString().contains(".pattern") }
            val = Transfer_S3Storage2Local.out.first()
            output = Convert_Concatenate2SingleOMETIFF(ch, val)
        }
        else {
            output = Convert_EachFile2SeparateOMETIFF(ch)
        }
    }
    else if ( params.source_type == "bia" ) {
        if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            chlist = Transfer_PrivateBiostudies2Local.out.collect()
            is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
            if ( is_auto && is_correctNames ) {
                pattern_files = createPatternFile1(Transfer_PrivateBiostudies2Local.out).flatten()
            }
            else {
                pattern_files = createPatternFile2(Transfer_PrivateBiostudies2Local.out).flatten()
            }
            ch = pattern_files.filter { it.toString().contains(".pattern") }
            val = Transfer_PrivateBiostudies2Local.out.first()
            output = Convert_Concatenate2SingleOMETIFF(ch, val)
        }
        else {
            output = Convert_EachFile2SeparateOMETIFF(ch)
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