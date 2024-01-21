#!/usr/bin/env nfprojects
nextflow.enable.dsl=2
// nextflow.enable.moduleBinaries = true

include { Convert2OMETIFF_FromLocal; Convert2OMETIFF_FromLocal_Merged; Convert2OMETIFF_FromLocal_CSV; Convert2OMETIFF_FromLocal_Merged_CSV } from "./modules/subworkflows_ometiff.nf"
include { Convert2OMETIFF_FromS3; Convert2OMETIFF_FromS3_Merged; Convert2OMETIFF_FromS3_CSV; Convert2OMETIFF_FromS3_Merged_CSV } from "./modules/subworkflows_ometiff.nf"
include { CreatePatternFile1; CreatePatternFile2; CreatePatternFileFromCsv;
          Convert_Concatenate2SingleOMETIFF; Convert_EachFile2SeparateOMETIFF; Convert_EachFileFromRoot2SeparateOMETIFF;
          Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local; Transfer_S3Storage2Local; Mirror_S3Storage2Local; Inspect_S3Path;
          Transfer_Local2S3Storage; Transfer_Local2S3Storage as Transfer_CSV2S3Storage; Transfer_Local2PrivateBiostudies;
          Csv2Symlink1; Csv2Symlink2; ParseCsv; UpdateCsv } from "./modules/processes.nf"
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList; get_filenames_fromList; verify_filenames_fromCsv; is_csv} from "./modules/functions.nf"

workflow {
    if  ( ( params.source_type == "local" ) && ( params.merge_files == "True" ) && ( is_csv(params.in_path) ) ) {
        // local && merged && CSV => input must be a file
        Convert2OMETIFF_FromLocal_Merged_CSV()
    }
    else if  ( ( params.source_type == "local" ) && ( params.merge_files == "True" ) ) {
        // local && merged &! CSV => input must be a directory
        Convert2OMETIFF_FromLocal_Merged()
    }
    else if  ( ( params.source_type == "local" ) && ( is_csv(params.in_path) ) ) {
        // local &! merged && CSV => input must be a file
        Convert2OMETIFF_FromLocal_CSV()
    }
    else if ( params.source_type == "local" ) {
        Convert2OMETIFF_FromLocal()
    }
    /////////////////////////////////////////////////////////
    else if  ( ( params.source_type == "s3" ) && ( params.merge_files == "True" ) && ( is_csv(params.in_path) ) ) {
        // local && merged && CSV => input must be a file
        Convert2OMETIFF_FromS3_Merged_CSV()
    }
    else if  ( ( params.source_type == "s3" ) && ( params.merge_files == "True" ) ) {
        // local && merged &! CSV => input must be a directory
        Convert2OMETIFF_FromS3_Merged()
    }
    else if  ( ( params.source_type == "s3" ) && ( is_csv(params.in_path) ) ) {
        // local &! merged && CSV => input must be a file
        Convert2OMETIFF_FromS3_CSV()
    }
    else if ( params.source_type == "s3" ) {
        Convert2OMETIFF_FromS3()
    }
    else {
        println("Unknown condition encountered. Check the main command line starting with 'batchconvert'.")
    }
}