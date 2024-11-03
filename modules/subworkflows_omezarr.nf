#!/usr/bin/env nflow
nextflow.enable.dsl=2
import groovy.io.FileType
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.Paths
import org.apache.commons.io.FileUtils

include { CreatePatternFile1; CreatePatternFile2; CreatePatternFileFromCsv;
          Convert_Concatenate2SingleOMEZARR; Convert_EachFile2SeparateOMEZARR; Convert_EachFileFromRoot2SeparateOMEZARR;
          Transfer_PrivateBiostudies2Local; Transfer_PublicBiostudies2Local; Transfer_S3Storage2Local; Mirror_S3Storage2Local; Inspect_S3Path;
          Transfer_Local2S3Storage; Transfer_Local2S3Storage as Transfer_CSV2S3Storage; Transfer_Local2PrivateBiostudies; Transfer_Local2PrivateBiostudies as Transfer_CSV2PrivateBiostudies;
          Csv2Symlink1; Csv2Symlink2; ParseCsv; UpdateCsv; UpdateCsvForConversion; InputPath2Symlink } from "./processes.nf"
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList; get_filenames_fromList; verify_filenames_fromCsv; is_csv; parse_path_for_remote} from "./functions.nf"

workflow GetS3Directory_AsChannel {
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
    emit:
    ch1f
    ch
}

workflow GetS3PathsFromCSV_AsChannel {
    main:
    ch_ = Channel.fromPath(params.in_path).splitCsv( header:true )
    if (params.root_column == 'auto') {
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
    emit:
    ch1f
    ch
}

workflow FromS3ToSymlinks { // This subworkflow is not to be directly incorporated in the main workflows
    // TODO: This workflow should be integrated with the InputPath2Symlink process
    main:
    if ( ( is_csv(params.in_path) ) ) {
        GetS3PathsFromCSV_AsChannel()
        ch1f = GetS3PathsFromCSV_AsChannel.out.ch1f
        ch = GetS3PathsFromCSV_AsChannel.out.ch
    } else {
        GetS3Directory_AsChannel()
        ch1f = GetS3Directory_AsChannel.out.ch1f
        ch = GetS3Directory_AsChannel.out.ch
    }
    localImages = ch.flatten().map { it -> file(it.toString()) }.unique()
    // Select a tempdir location
    parent = localImages.flatten().map { it -> file(it.parent.parent.parent.toString()) }.unique()
    ch_s = parent.first().map { dir -> dir.toString() + '/temp' }
    //
    ch_s.subscribe { targetDir ->
        // Ensure the tempdir is freshly created before creating symlinks
        new File(targetDir).mkdirs()
        if ( file(targetDir).isDirectory() ) {
            FileUtils.cleanDirectory(new File(targetDir))
            file(targetDir).mkdirs()
        }
        else {
            new File(targetDir).mkdirs()
        }
        // Subscribe to `localImages` channel to create symlinks for each file
        localImages.subscribe { fileDir ->
            symlinkPath = file(targetDir + '/' + fileDir.Name) // Path for the symlink
            // println("Creating symlink for ${fileDir} -> ${symlinkPath}")
            Files.createSymbolicLink(symlinkPath, fileDir)
        }
    }
    ch_f = ch_s.map { it ->
        file(it)
    }
    emit:
    ch_f
    localImages
}

workflow Convert2OMEZARR_FromLocal {
    main:
    InputPath2Symlink()
    ch_s = InputPath2Symlink.out.symlinkpath
    ch = ch_s.listFiles().flatten().filter{ it.isFile() }
    output = Convert_EachFileFromRoot2SeparateOMEZARR(ch_s, ch)
    if (params.dest_type == "s3") {
        Transfer_Local2S3Storage(output)
    }
    else if ( params.dest_type == "bia" ) {
        Transfer_Local2PrivateBiostudies(output)
    }
    emit:
    output
}

workflow Convert2OMEZARR_FromS3 { // s3 &! merged &! CSV
    main:
    FromS3ToSymlinks()
    fpath = FromS3ToSymlinks.out.ch_f
    ch = FromS3ToSymlinks.out.localImages
    output = Convert_EachFileFromRoot2SeparateOMEZARR(fpath, ch)
    if (params.dest_type == "s3") {
        Transfer_Local2S3Storage(output)
    }
    else if ( params.dest_type == "bia" ) {
        Transfer_Local2PrivateBiostudies(output)
    }
    emit:
    output
}

workflow Convert2OMEZARR_FromLocal_Merged { // local && merged &! CSV
    main:
    InputPath2Symlink()
    ch_f = InputPath2Symlink.out.symlinkpath
    fpath = ch_f.map { it ->
        file(it).toString()
    }
    is_auto = verify_axes(params.concatenation_order)
    if ( params.metafile.size() > 0 ) { // TODO for csv !!!
        pattern_files = Channel.fromPath( params.metafile ).flatten()
        ch = pattern_files
    }
    else if ( is_auto ) {
        pattern_files = CreatePatternFile1(fpath).flatten()
        ch = pattern_files.filter { it.toString().contains(".pattern") }
    }
    else {
        pattern_files = CreatePatternFile2(fpath).flatten()
        ch = pattern_files.filter { it.toString().contains(".pattern") }
    }
    output = Convert_Concatenate2SingleOMEZARR(ch, fpath)
    if (params.dest_type == "s3") {
        Transfer_Local2S3Storage(output)
    }
    else if ( params.dest_type == "bia" ) {
        Transfer_Local2PrivateBiostudies(output)
    }
}

workflow Convert2OMEZARR_FromS3_Merged { // s3 && merged &! CSV
    main:
    FromS3ToSymlinks()
    fpath = FromS3ToSymlinks.out.ch_f
    is_auto = verify_axes(params.concatenation_order)
    if ( fpath.isDirectory() ) {
        if ( params.metafile.size() > 0 ) { // TODO for csv !!!
            pattern_files = Channel.fromPath( params.metafile ).flatten()
            ch = pattern_files
        }
        else if ( is_auto ) {
            pattern_files = CreatePatternFile1(fpath).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        else {
            pattern_files = CreatePatternFile2(fpath).flatten()
            ch = pattern_files.filter { it.toString().contains(".pattern") }
        }
        output = Convert_Concatenate2SingleOMEZARR(ch, fpath)
        if (params.dest_type == "s3") {
            Transfer_Local2S3Storage(output)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
        }
    }
    else {
        output = null
        println(" Convert2OMEZARR_Input path must be either a directory or a csv file. ")
    }
    emit:
    output
}

workflow Convert2OMEZARR_FromLocal_CSV { // local &! merged && CSV
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Wildcards cannot be applied to csv files. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        ch = Csv2Symlink1( params.in_path, params.root_column, params.input_column, 'symlinks' ).flatten()
        output = Convert_EachFile2SeparateOMEZARR(ch)
        if ( params.dest_type == "s3" ) {
            Transfer_Local2S3Storage(output)
        }
        else if ( params.dest_type == "bia" ) {
            Transfer_Local2PrivateBiostudies(output)
        }
    }
    emit:
    output
}

workflow Convert2OMEZARR_FromS3_CSV { // s3 &! merged && CSV
    /// Note that this subworkflow does not support concurrency for multi-file formats such as vsi.
    /// Consider another subworkflow, which uses mirroring for data transfer.
    main:
    if ( params.in_path.toString().contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Wildcards cannot be applied to csv files. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
    }
    else {
        GetS3PathsFromCSV_AsChannel()
        ch = GetS3PathsFromCSV_AsChannel.out.ch
        output = Convert_EachFile2SeparateOMEZARR(ch)
        mock = output.collect().flatten().first()
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

workflow Convert2OMEZARR_FromLocal_Merged_CSV {
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Wildcards cannot be applied to csv files. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
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
        output = Convert_Concatenate2SingleOMEZARR(ch, Csv2Symlink2.out)
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

workflow Convert2OMEZARR_FromS3_Merged_CSV { // S3 && CSV && MERGE_FILES
    main:
    if ( params.in_path.contains( "*" ) ) {
        println( "\u001B[31m"+"Error: Wildcards cannot be applied to csv files. Try using '--pattern' or '-p' argument to filter input files with patterns."+"\u001B[30m" )
        println( "Workflow being killed." )
        return
    }
    else {
        FromS3ToSymlinks()
        fpath = FromS3ToSymlinks.out.ch_f
        is_auto = verify_axes(params.concatenation_order)
        if ( fpath.isDirectory() ) {
            if ( params.metafile.size() > 0 ) { // TODO for csv !!!
                pattern_files = Channel.fromPath( params.metafile ).flatten()
                ch = pattern_files
            }
            else if ( is_auto ) {
                pattern_files = CreatePatternFile1(fpath).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            else {
                pattern_files = CreatePatternFile2(fpath).flatten()
                ch = pattern_files.filter { it.toString().contains(".pattern") }
            }
            output = Convert_Concatenate2SingleOMEZARR(ch, fpath)
            if (params.dest_type == "s3") {
                Transfer_Local2S3Storage(output)
            }
            else if ( params.dest_type == "bia" ) {
                Transfer_Local2PrivateBiostudies(output)
            }
        }
        else {
            output = null
            println(" Convert2OMEZARR_Input path must be either a directory or a csv file. ")
        }
    }
    emit:
    output
}


