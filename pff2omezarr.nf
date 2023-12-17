#!/usr/bin/env nfprojects
nextflow.enable.dsl=2
// nextflow.enable.moduleBinaries = true

include { createPatternFile1; createPatternFile2; createPatternFileFromCsv; Convert_Concatenate2SingleOMEZARR; Convert_EachFile2SeparateOMEZARR; Convert_EachFileFromRoot2SeparateOMEZARR; Transfer_Local2S3Storage; Transfer_S3Storage2Local; Mirror_S3Storage2Local; Transfer_Local2PrivateBiostudies; Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local; Inspect_S3Path; Csv2Symlink1; Csv2Symlink2; ParseCsv } from "./modules/modules.nf"
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList; get_filenames_fromList; verify_filenames_fromCsv; is_csv} from "./modules/modules.nf"

workflow {
    // If the input dataset is in s3 or bia, bring it to the execution environment first:
    // Note that this scenario assumes that the input path corresponds to a directory at s3 (not a single file)
    if ( params.source_type == "s3" ) {
        if ( params.in_path.toString().contains( "*" ) ) {
            println( "\u001B[31m"+"Error: Globbing cannot be used with remote files. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        }
        else if ( is_csv( params.in_path ) && ( params.merge_files == "True" ) ) { // S3 && CSV && MERGE_FILES
            def fpath = file(params.in_path)
            parsedCsv = ParseCsv( fpath.toString(), params.root_column, params.input_column, 'parsed' )
//             checkCsv(fpath)
            ch_ = ParseCsv.out.
                          splitCsv(header:true)
            ch00 = ch_.map { row -> row[params.root_column] }.unique()
            ch0 = Mirror_S3Storage2Local(ch00)
        }
        else if ( is_csv( params.in_path ) ) { // S3 && CSV && !! MERGE_FILES. Note that this branch does not support concurrency for multi-file formats such as vsi.
            def fpath = file(params.in_path)
            ch_ = Channel.fromPath(fpath.toString()).
                            splitCsv(header:true)
            if (params.root_column == 'auto'){
                ch0 = ch_.map { row-> params.S3REMOTE + '/' + params.S3BUCKET + '/' + row[params.input_column] }
            }
            else {
                ch0 = ch_.map { row-> params.S3REMOTE + '/' + params.S3BUCKET + '/' + row[params.root_column] + '/' + row[params.input_column] }
            }
//             ch0 = ch00.flatMap { it.toString().split('\n') }
            ch1 = ch0.filter { it.toString().contains(params.pattern) }
            if ( params.reject_pattern.size() > 0 ) {
                ch1 = ch1.filter { !(it.toString().contains(params.reject_pattern)) }
            }
            ch1f = ch1.flatMap { file(it).Name }
            ch = Transfer_S3Storage2Local(ch1, ch1f)
        }
        else if ( params.merge_files == "True" ) { // S3 && ! CSV && MERGE_FILES
            ch00 = Channel.of(params.in_path)
            ch0 = Mirror_S3Storage2Local(ch00)
        }
        else { // // S3 && ! CSV && ! MERGE_FILES This branch will be deleted, no concurrency for import as it jeopardises conversion for multi-file formats.
            ch000 = Channel.of(params.in_path)
            Inspect_S3Path(ch000)
            ch00 = Inspect_S3Path.out.filelist
            ch0 = ch00.flatMap { it.toString().split('\n') }
            ch1 = ch0.filter { it.toString().contains(params.pattern) }
            if ( params.reject_pattern.size() > 0 ) {
                ch1 = ch1.filter { !(it.toString().contains(params.reject_pattern)) }
            }
            ch1f = ch1.flatMap { file(it).Name }
            ch = Transfer_S3Storage2Local(ch1, ch1f)
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
        def fpath = file(params.in_path)
        if ( ( params.merge_files == "True" ) && ( fpath.isFile() ) ) {// Note that reading file paths from csv file is currently only possible if data is local.
            if ( fpath.toString().endsWith('.csv') || fpath.toString().endsWith('.txt') ) {
                ch0 = Csv2Symlink2( fpath, params.root_column, params.input_column, 'symlinks' ).collect()
                imgpath = Csv2Symlink2.out
                ch = "NULL"
            }
            else {
                imgpath = fpath
                ch = "NULL"
            }
        }
        else if ( ( params.merge_files == "True" ) ) {
            fpath = Channel.of(params.in_path)
            imgpath = fpath
        }
        else {
            // Note the above assignment yields either a list of files (with globbing), a single file (if the parameter in_path corresponds to a file path) a directory (if the parameter in_path corresponds to a directory path)
            // Make sure a proper channel is created in any of these 3 cases:
            if  ( fpath instanceof List ){
                ch1 = Channel.fromPath(params.in_path).filter { it.toString().contains(params.pattern) }
            }
            else if ( fpath.isDirectory() ) {
                ch0 = Channel.of(fpath.listFiles()).flatten()
                ch1 = ch0.filter { it.toString().contains(params.pattern) }
            }
            else if ( fpath.isFile() ) { // Note that reading file paths from csv file is currently only possible if data is local.
                if ( fpath.toString().endsWith('.csv') || fpath.toString().endsWith('.txt') ){
                    ch0 = Csv2Symlink1( fpath, params.root_column, params.input_column, 'symlinks' ).flatten()
                }
                else {
                    ch0 = Channel.of(fpath).collect().flatten()
                }

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
        def fpath = file(params.in_path)
        // Create a branch leading either to a grouped conversion or one-to-one conversion.
        if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            if  ( is_csv( fpath.toString() ) ) {
                is_correctNames = verify_filenames_fromCsv(fpath, params.pattern, params.reject_pattern,
                                                            params.root_column, params.input_column)
            }
            else if ( fpath.isDirectory() ) {
                is_correctNames = verify_filenames_fromPath(fpath.toString(), params.pattern, params.reject_pattern)
            }
            else {
                println(" Input path must be either a directory or a csv file. ")
            }
            if ( params.metafile.size() > 0 ) { // TODO for csv !!!!!!!!!!!!!!!!!!!!!!!!
                pattern_files = Channel.fromPath( params.metafile ).flatten()
                ch = pattern_files
            }
            else if ( is_auto && is_correctNames &&  is_csv( fpath.toString() ) ) {
                pattern_files = createPatternFile1(imgpath).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else if ( is_auto && is_correctNames ) {
                imgpath = fpath
                pattern_files = createPatternFile1(fpath).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else if ( is_csv( fpath.toString() )  ) {
                pattern_files = createPatternFile2(imgpath).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else {
                println("Or we are here indeed.")
                imgpath = params.in_path
                pattern_files = createPatternFile2(params.in_path).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
//             ch.view()
            output = Convert_Concatenate2SingleOMEZARR(ch, imgpath)
        }
        else {
            if ( is_csv( fpath.toString() ) ) {
                output = Convert_EachFile2SeparateOMEZARR(ch)
            }
            else {
                output = Convert_EachFileFromRoot2SeparateOMEZARR(params.in_path, ch)
            }
        }
    }
    else if ( params.source_type == "s3" ) {
        def fpath = file(params.in_path)
        // Create a branch leading either to a grouped conversion or one-to-one conversion.
        if ( fpath.toString().contains( "*" ) ) {
            println( "Workflow being killed." )
        }
        else if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            chlist = ch0.collect()
            is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
            // println(params.metafile.size())
            if ( params.metafile.size() > 0 ) {
                pattern_files = Channel.fromPath( params.metafile ).flatten()
                ch = pattern_files
            }
            else if ( is_auto && is_correctNames && is_csv( fpath.toString() ) ) {   // S3 && CSV && MERGE_FILES
                pattern_files = createPatternFileFromCsv(ch0, parsedCsv, params.input_column).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else if ( is_auto && is_correctNames ) {
                pattern_files = createPatternFile1(Mirror_S3Storage2Local.out).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else if ( is_csv( fpath.toString() )  ) {
                pattern_files = createPatternFileFromCsv(ch0, parsedCsv, params.input_column).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else {
                pattern_files = createPatternFile2(Mirror_S3Storage2Local.out).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            val = Mirror_S3Storage2Local.out.first()
            output = Convert_Concatenate2SingleOMEZARR(ch, val)
        }
        else {
            output = Convert_EachFile2SeparateOMEZARR(ch) // Note that the conversion is not from root.
        }
    }
    else if ( params.source_type == "bia" ) {
        if ( params.merge_files == "True" ) {
            is_auto = verify_axes(params.concatenation_order)
            chlist = Transfer_PrivateBiostudies2Local.out.collect()
            is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
//             println(params.metafile.size())
            if ( params.metafile.size() > 0 ) {
                pattern_files = Channel.fromPath( params.metafile ).flatten()
                ch = pattern_files
            }
            else if ( is_auto && is_correctNames ) {
                pattern_files = createPatternFile1(Transfer_PrivateBiostudies2Local.out).flatten()
            }
            else {
                pattern_files = createPatternFile2(Transfer_PrivateBiostudies2Local.out).flatten()
            }
            ch = pattern_files.filter { it.toString().contains(".pattern") }
            val = Transfer_PrivateBiostudies2Local.out.first()
            output = Convert_Concatenate2SingleOMEZARR(ch, val)
        }
        else {
            output = Convert_EachFile2SeparateOMEZARR(ch) // Note that the conversion is not from root.
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
