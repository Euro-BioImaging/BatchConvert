#!/usr/bin/env nflow
nextflow.enable.dsl=2
import groovy.io.FileType

include { CreatePatternFile1; CreatePatternFile2; CreatePatternFileFromCsv;
          Convert_Concatenate2SingleOMETIFF; Convert_EachFile2SeparateOMETIFF; Convert_EachFileFromRoot2SeparateOMETIFF;
          Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local; Transfer_S3Storage2Local; Mirror_S3Storage2Local; Inspect_S3Path;
          Transfer_Local2S3Storage; Transfer_Local2S3Storage as Transfer_CSV2S3Storage; Transfer_Local2PrivateBiostudies; Transfer_Local2PrivateBiostudies as Transfer_CSV2PrivateBiostudies;
          Csv2Symlink1; Csv2Symlink2; ParseCsv; UpdateCsv } from "./processes.nf"
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList; get_filenames_fromList; verify_filenames_fromCsv; is_csv; parse_path_for_remote} from "./functions.nf"

workflow Convert2OMETIFF_FromLocal {
    main:
    def fpath = file(params.in_path)
    if  ( fpath instanceof List ){
        ch = Channel.fromPath(params.in_path).filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        output = Convert_EachFileFromRoot2SeparateOMETIFF(params.in_path, ch)
    }
    else if ( fpath.isDirectory() ) { // local && ! csv && ! merge_files
        ch0 = Channel.of(fpath.listFiles()).flatten()
        ch = ch0.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        output = Convert_EachFileFromRoot2SeparateOMETIFF(params.in_path, ch)
    }
    else if ( fpath.isFile() ) { // local && ! csv && ! merge_files
        ch0 = Channel.of(fpath).collect().flatten()
        ch = ch0.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        output = Convert_EachFile2SeparateOMETIFF(ch)
    }
    // ch1 must be acquired by this point based on the 3 cases above, now apply reject_pattern filter
    if (params.dest_type == "s3") {
        Transfer_Local2S3Storage(output)
    }
    else if ( params.dest_type == "bia" ) {
        Transfer_Local2PrivateBiostudies(output)
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromS3 {
    main:
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
    output = Convert_EachFile2SeparateOMETIFF(ch)
    if (params.dest_type == "s3") {
        Transfer_Local2S3Storage(output)
    }
    else if ( params.dest_type == "bia" ) {
        Transfer_Local2PrivateBiostudies(output)
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromLocal_Merged { // local && merged &! CSV
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used together with '--merge_files' option. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        def fpath = file(params.in_path)
        is_auto = verify_axes(params.concatenation_order)
        if ( fpath.isDirectory() ) {
            is_correctNames = verify_filenames_fromPath(fpath.toString(), params.pattern, params.reject_pattern)
            if ( params.metafile.size() > 0 ) { // TODO for csv !!!
                pattern_files = Channel.fromPath( params.metafile ).flatten()
                ch = pattern_files
            }
            else if ( is_auto && is_correctNames ) {
                pattern_files = CreatePatternFile1(fpath).flatten()
//                 pattern_files.view()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else {
                pattern_files = CreatePatternFile2(params.in_path).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            output = Convert_Concatenate2SingleOMETIFF(ch, params.in_path)
            if (params.dest_type == "s3") {
                Transfer_Local2S3Storage(output)
            }
            else if ( params.dest_type == "bia" ) {
                Transfer_Local2PrivateBiostudies(output)
            }
        }
        else {
            println(" Convert2OMETIFF_Input path must be either a directory or a csv file. ")
            return
        }
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromS3_Merged { // s3 && merged &! CSV
    main:
    if ( params.in_path.toString().contains( "**" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used with '--merge_files' option. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
    }
    else {
        ch00 = Channel.of(params.in_path)
        ch0 = Mirror_S3Storage2Local(ch00)
        is_auto = verify_axes(params.concatenation_order)
        chlist = ch0.collect()
        is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
        if ( params.metafile.size() > 0 ) {
            pattern_files = Channel.fromPath( params.metafile ).flatten()
            ch = pattern_files
        }
        else if ( is_auto && is_correctNames ) {
            pattern_files = CreatePatternFile1(Mirror_S3Storage2Local.out).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        else {
            pattern_files = CreatePatternFile2(Mirror_S3Storage2Local.out).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        val = Mirror_S3Storage2Local.out.first()
        output = Convert_Concatenate2SingleOMETIFF(ch, val)
        if (params.dest_type == "s3") {
            Transfer_Local2S3Storage(output)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
        }
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromLocal_CSV { // s3 &! merged && CSV
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used together with CSV input."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        def fpath = file(params.in_path)
        parsedCsv = ParseCsv( fpath.toString(), params.root_column, params.input_column, 'parsed.txt' )
        ch0 = Csv2Symlink1( parsedCsv, "RootOriginal", "ImageNameOriginal", 'symlinks' ).flatten()
        ch1 = ch0.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch = ch1.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        else {
            ch = ch1
        }
        output = Convert_EachFile2SeparateOMETIFF(ch)
        mock = output.collect().flatten().first()
        UpdateCsv(parsedCsv, "RootOriginal", "ImageNameOriginal", "ometiff", mock)
        if ( params.dest_type == "s3" ) {
            Transfer_Local2S3Storage(output)
            Transfer_CSV2S3Storage(UpdateCsv.out)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
            Transfer_CSV2S3Storage(UpdateCsv.out)
        }
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromS3_CSV { // s3 &! merged && CSV
    /// Note that this subworkflow does not support concurrency for multi-file formats such as vsi.
    /// Consider another subworkflow, which uses mirroring for data transfer.
    main:
    if ( params.in_path.toString().contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used with CSV input. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
    }
    else {
        def fpath = file(params.in_path)
//         println(fpath)
        parsedCsv = ParseCsv( fpath.toString(), params.root_column, params.input_column, 'parsed.txt' ) // CAREFUL!
        ch_ = Channel.fromPath(fpath.toString()).
                        splitCsv(header:true)
        if (params.root_column == 'auto'){
            ch0 = ch_.map { row-> params.S3REMOTE + '/' + params.S3BUCKET + '/' + row[params.input_column] }
        }
        else {
            ch0 = ch_.map { row-> params.S3REMOTE + '/' + params.S3BUCKET + '/' + row[params.root_column] + '/' + row[params.input_column] }
        }
        ch1 = ch0.filter { it.toString().contains(params.pattern) }
        if ( params.reject_pattern.size() > 0 ) {
            ch1 = ch1.filter { !(it.toString().contains(params.reject_pattern)) }
        }
        ch1f = ch1.flatMap { file(it).Name }
        ch = Transfer_S3Storage2Local(ch1, ch1f)
        output = Convert_EachFile2SeparateOMETIFF(ch)
        UpdateCsv(parsedCsv, "RootOriginal", "ImageNameOriginal", "ometiff")
        if (params.dest_type == "s3") {
            Transfer_Local2S3Storage(output)
            Transfer_CSV2S3Storage(UpdateCsv.out)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
            Transfer_CSV2PrivateBiostudies(UpdateCsv.out)
        }
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromLocal_Merged_CSV {
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used together with '--merge_files' option. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        def fpath = file(params.in_path)
        is_auto = verify_axes(params.concatenation_order)
        ch0 = Csv2Symlink2( fpath, params.root_column, params.input_column, 'symlinks' ).collect()
        ch = "NULL"
        is_correctNames = verify_filenames_fromCsv(fpath, params.pattern, params.reject_pattern,
                                                    params.root_column, params.input_column)
        if ( is_auto && is_correctNames ) {
            pattern_files = CreatePatternFile1(Csv2Symlink2.out).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        else {
            pattern_files = CreatePatternFile2(Csv2Symlink2.out).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        output = Convert_Concatenate2SingleOMETIFF(ch, Csv2Symlink2.out)
        if (params.dest_type == "s3") {
            Transfer_Local2S3Storage(output)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
        }
    }
    emit:
    output
}

workflow Convert2OMETIFF_FromS3_Merged_CSV { // S3 && CSV && MERGE_FILES
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Globbing cannot be used together with '--merge_files' option. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        def fpath = file(params.in_path)
        parsedCsv = ParseCsv( fpath.toString(), params.root_column, params.input_column, 'parsed.txt' )
        ch_ = ParseCsv.out.
                      splitCsv(header:true)
        ch00 = ch_.map { row -> row["RootOriginal"] }.unique()
        ch0 = Mirror_S3Storage2Local(ch00)

        is_auto = verify_axes(params.concatenation_order)
        chlist = ch0.collect()
        is_correctNames = verify_filenames_fromList(chlist, params.pattern, params.reject_pattern)
        // println(params.metafile.size())
        if ( params.metafile.size() > 0 ) {
            pattern_files = Channel.fromPath( params.metafile ).flatten()
            ch = pattern_files
        }
        else if ( is_auto && is_correctNames ) {
            pattern_files = CreatePatternFileFromCsv(ch0, parsedCsv, "ImageNameOriginal").flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        else {
            pattern_files = CreatePatternFileFromCsv(ch0, parsedCsv, "ImageNameOriginal").flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        val = Mirror_S3Storage2Local.out.first()
        output = Convert_Concatenate2SingleOMETIFF(ch, val)
        if (params.dest_type == "s3") {
            Transfer_Local2S3Storage(output)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
        }
    }
    emit:
    output
}



