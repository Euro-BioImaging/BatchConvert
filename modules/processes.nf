#!/usr/bin/env nflow
nextflow.enable.dsl=2
import groovy.io.FileType
include { verify_axes; verify_filenames_fromPath; verify_filenames_fromList; get_filenames_fromList; verify_filenames_fromCsv; is_csv; parse_path_for_remote} from "./functions.nf"

// Note that you can update parameterisation steps as beforeScript directives

// Conversion processes

process Convert_EachFileFromRoot2SeparateOMETIFF {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        val root
    input:
        path inpath
    output:
        path "${inpath.baseName}.ome.tiff", emit: conv

    script:
    """
    ${params.binpath}/run_conversion.py "$root/$inpath" "${inpath.baseName}.ome.tiff"
    """
}

process Convert_EachFile2SeparateOMETIFF {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path inpath
    output:
        path "${inpath.baseName}.ome.tiff", emit: conv

    script:
    template 'makedirs.sh "${params.out_path}"'
    """
    ${params.binpath}/run_conversion.py "$inpath.name" "${inpath.baseName}.ome.tiff"
    """
}

process Convert_Concatenate2SingleOMETIFF {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path pattern_file
    input:
        val inpath
    output:
        path "${pattern_file.baseName}.ome.tiff", emit: conv
    script:
    template 'makedirs.sh "${params.out_path}"'
    """
    if [[ -d "${inpath}/tempdir" ]];
        then
            ${params.binpath}/run_conversion.py "${inpath}/tempdir/${pattern_file}" "${pattern_file.baseName}.ome.tiff"
        else
            ${params.binpath}/run_conversion.py "$inpath/$pattern_file.name" "${pattern_file.baseName}.ome.tiff"
    fi
    # rm -rf ${inpath}/tempdir &> /dev/null
    # rm -rf ${inpath}/*pattern &> /dev/null
    """
}

process Convert_EachFileFromRoot2SeparateOMEZARR {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        val root
    input:
        path inpath
    output:
        path "${inpath.baseName}.ome.zarr", emit: conv

    script:
    template 'makedirs.sh "${params.out_path}"'
    """
    if echo "$root" | grep -q "*";
        then
            ${params.binpath}/run_conversion.py "\$(dirname "$root")/$inpath" "${inpath.baseName}.ome.zarr"
        else
            ${params.binpath}/run_conversion.py "$root/$inpath" "${inpath.baseName}.ome.zarr"
    fi
    """
}

process Convert_EachFile2SeparateOMEZARR {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path inpath
    output:
        path "${inpath.baseName}.ome.zarr", emit: conv
    script:
    template 'makedirs.sh "${params.out_path}"'
    """
    ${params.binpath}/run_conversion.py "$inpath.name" "${inpath.baseName}.ome.zarr"
    """
}

process Convert_Concatenate2SingleOMEZARR{
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    // This process will be probably changed completely. Create hyperstack will probably be a different process
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path pattern_file
    input:
        val inpath
    output:
        path "${pattern_file.baseName}.ome.zarr", emit: conv
    script:
    template 'makedirs.sh "${params.out_path}"'
    """
    if [[ -d "${inpath}/tempdir" ]];
        then
            ${params.binpath}/run_conversion.py "${inpath}/tempdir/${pattern_file.name}" "${pattern_file.baseName}.ome.zarr"
        else
            ${params.binpath}/run_conversion.py "$inpath/$pattern_file.name" "${pattern_file.baseName}.ome.zarr"
    fi
    # rm -rf ${inpath}/tempdir &> /dev/null
    # rm -rf ${inpath}/*pattern &> /dev/null
    """
}

// Processes for inspecting a remote location:

process Inspect_S3Path {
    // TODO: add pattern filtering to this process and remove it from the relevant subworkflows
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val source
    output:
        stdout emit: filelist
    script:
    contains = (!params.containsKey('pattern') || params.pattern == null || params.pattern == 'None') ? "\"\"" : params.pattern
    ignores = (!params.containsKey('reject_pattern') || params.reject_pattern == null || params.reject_pattern == 'None') ? "\"\"" : params.reject_pattern
    """
    sleep 5;
    mc -C "./mc" alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}" &> /dev/null;
    parse_s3_filenames.py "${params.S3REMOTE}/${params.S3BUCKET}/${source}/" --contains "${contains}" --excludes "${ignores}"
    """
}

// Transfer processes:

process Transfer_Local2S3Storage {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        path local
    output:
        path "./transfer_report.txt", emit: tfr
    script:
    def out_path = parse_path_for_remote(params.out_path)
    """
    sleep 5;
    localname="\$(basename $local)" && \
    mc -C "./mc" alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    if [ -f $local ];then
        mc -C "./mc" cp $local "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${out_path}"/"\$localname";
    elif [ -d $local ];then
        mc -C "./mc" mirror $local "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${out_path}"/"\$localname";
    fi
    echo "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${out_path}"/$local > "./transfer_report.txt";
    """
}

process Mirror_S3Storage2Local {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val source
    output:
        path "transferred/${source}"
    script:
    """
    sleep 5;
    mc -C "./mc" alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    mc -C "./mc" mirror "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${source}" "transferred/${source}";
    """
}


process Transfer_S3Storage2Local {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val s3path
        val s3name
    output:
        path "${s3name}"
    script:
    """
    sleep 5;
    mc -C "./mc" alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    mc -C "./mc" cp "${s3path}" "${s3name}";
    """
}

process Transfer_Local2PrivateBiostudies {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        path local
    output:
        path "./transfer_report.txt", emit: tfr
    script:
    def out_path = parse_path_for_remote(params.out_path)
    """
    ascp -P33001 -l 500M -k 2 -i $BIA_SSH_KEY -d $local bsaspera_w@hx-fasp-1.ebi.ac.uk:${params.BIA_REMOTE}/${out_path};
    echo "${params.BIA_REMOTE}"/"${out_path}" > "./transfer_report.txt";
    """
}

process Transfer_PrivateBiostudies2Local {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val source
    output:
        path "${source}"
    script:
    // source un basename ini ascp nin output kismina yerlestir
    """
    ascp -P33001 -l 500M -k 2 -i $BIA_SSH_KEY -d bsaspera_w@hx-fasp-1.ebi.ac.uk:${params.BIA_REMOTE}/$source ".";
    """
}

process Transfer_PublicBiostudies2Local {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val source
    output:
        path transferred
    script:
    // source un basename ini ascp nin output kismina yerlestir
    """
    ascp -P33001 -i $BIA_SSH_KEY bsaspera@fasp.ebi.ac.uk:$source transferred;
    """
}

process CreatePatternFile1 {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        path inpath
    output:
        path "${inpath}/*"
    script:
    """
    if [[ "${params.pattern}" == '' ]] && [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} ${inpath}
    elif [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} ${inpath}
    elif [[ "${params.pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --reject_by ${params.reject_pattern} ${inpath}
    else
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} --reject_by ${params.reject_pattern} ${inpath}
    fi
    """
}

process CreatePatternFile2 {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        path inpath
    output:
        path "${inpath}/tempdir/*"
    script:
    """
    if [[ "${params.pattern}" == '' ]] && [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} ${inpath}
    elif [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} ${inpath}
    elif [[ "${params.pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --reject_by ${params.reject_pattern} ${inpath}
    else
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} --reject_by ${params.reject_pattern} ${inpath}
    fi
    """
}

process CreatePatternFileFromCsv {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        path inpath //
    input:
        path use_list // This has to be the path to the csv file
    input:
        val colname // This is the name of the csv column
    output:
        path "${inpath}/tempdir/*"
    script:
    """
    if [[ "${params.pattern}" == '' ]] && [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --use_list ${use_list} --colname ${colname} ${inpath}
    elif [[ "${params.reject_pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} --use_list ${use_list} --colname ${colname} ${inpath}
    elif [[ "${params.pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} --reject_by ${params.reject_pattern} --use_list ${use_list} --colname ${colname} ${inpath}
    else
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} --reject_by ${params.reject_pattern} --use_list ${use_list} --colname ${colname} ${inpath}
    fi
    """
}

process InputPath2Symlink {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    output:
        path "symlinks", emit: symlinkpath
    script:
    contains = (!params.containsKey('pattern') || params.pattern == null || params.pattern == 'None') ? "\"\"" : params.pattern
    ignores = (!params.containsKey('reject_pattern') || params.reject_pattern == null || params.reject_pattern == 'None') ? "\"\"" : params.reject_pattern
    if ( params.containsKey('merge_files') ) {
        files_only = params.merge_files
    } else {
        files_only = 'False'
    }
    """
    directory2symlink.py "${params.in_path}" \
    --contains "${contains}" \
    --ignores "${ignores}" \
    --files_only $files_only
    """
}

process Csv2Symlink2 {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val csv_path
    input:
        val root_column
    input:
        val input_column
    input:
        val dest_path
    output:
        path "${dest_path}"
    script:
    contains = (!params.containsKey('pattern') || params.pattern == null || params.pattern == 'None') ? "\"\"" : params.pattern
    ignores = (!params.containsKey('reject_pattern') || params.reject_pattern == null || params.reject_pattern == 'None') ? "\"\"" : params.reject_pattern
    """
    csv2symlink.py $csv_path $root_column $input_column $dest_path \
    --contains "${contains}" \
    --ignores "${ignores}"
    """
}

process Csv2Symlink1 {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val csv_path
    input:
        val root_column
    input:
        val input_column
    input:
        val dest_path
    output:
        path "${dest_path}/*"
    script:
    contains = (!params.containsKey('pattern') || params.pattern == null || params.pattern == 'None') ? "\"\"" : params.pattern
    ignores = (!params.containsKey('reject_pattern') || params.reject_pattern == null || params.reject_pattern == 'None') ? "\"\"" : params.reject_pattern
    """
    csv2symlink.py $csv_path $root_column $input_column $dest_path \
    --contains "${contains}" \
    --ignores "${ignores}"
    """
}

process ParseCsv {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    input:
        val csv_path
    input:
        val root_column
    input:
        val input_column
    input:
        val dest_path
    input:
        val endpoint
    output:
        path "${dest_path}"
    script:
    contains = (!params.containsKey('pattern') || params.pattern == null || params.pattern == 'None') ? "\"\"" : params.pattern
    ignores = (!params.containsKey('reject_pattern') || params.reject_pattern == null || params.reject_pattern == 'None') ? "\"\"" : params.reject_pattern
    """
    parse_csv.py $csv_path "${dest_path}" $root_column $input_column \
    -p "${contains}" \
    -rp "${ignores}" \
    --endpoint $endpoint
    """
}

process UpdateCsv {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path csv_path
    input:
        val root_column
    input:
        val input_column
    input:
        val conversion_type
    input:
        path proof_of_files
    output:
        path "FileList.csv"
    script:
    """
    update_csv.py $csv_path $root_column $input_column "${params.out_path}" "FileList.csv" --conversion_type $conversion_type
    """
}

process UpdateCsvForConversion {
    sleep 1000
    errorStrategy { sleep(Math.pow(2, task.attempt) * 200 as long); return 'retry' }
    maxRetries 5
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path csv_path
    input:
        val root_column
    input:
        val input_column
    input:
        val conversion_type
    input:
        path proof_of_files
    output:
        path "FileList.csv"
    script:
    """
    update_csv_for_conversion.py $csv_path $root_column $input_column "${params.out_path}" "FileList.csv" --conversion_type $conversion_type
    """
}


// EXPERIMENTAL PROCESSES THAT ARE CURRENTLY NOT NEEDED

//
// process cleanup {
//     input:
//         path inpath
//     script:
//     """
//     rm -rf "${inpath}/tempdir" &> /dev/null
//     rm -rf "${inpath}/*pattern" &> /dev/null
//     """
// }
//
// process mirror2local {
//     input:
//         val source
//     output:
//         path "transferred"
//     script:
//     """
//     mc alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
//     mc mirror "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${source}" "transferred";
//     """
// }
//
// process stageLocal {
//     input:
//         path filepath
//     output:
//         path "${filepath.baseName}"
//     """
//     """
// }
//
// process stageLocalPublish {
//     if ("${params.dest_type}"=="local") {
//         publishDir(
//             path: "${params.out_path}",
//             mode: 'copy'
//         )
//     }
//     input:
//         path filepath
//     output:
//         path "${filepath.baseName}"
//     """
//     """
// }
//
// process bioformats2raw_experimental {
//     if ("${params.dest_type}"=="local") {
//         publishDir(
//             path: "${params.out_path}",
//             mode: 'copy'
//         )
//     }
//     input:
//         path inpath
//     output:
//         path "${inpath.baseName}.ome.zarr", emit: conv
//     script:
//     template 'makedirs.sh "${params.out_path}"'
//     """
//     if [[ "${params.merge_files}" == "True" ]];
//         then
//             create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} ${inpath};
//             if [[ "${params.concatenation_order}" == "auto" ]];
//                 then
//                     ${params.binpath}/run_conversion.py $inpath/*pattern "${inpath.baseName}.ome.zarr"
//             elif ! [[ "${params.concatenation_order}" == "auto" ]];
//                 then
//                     ${params.binpath}/run_conversion.py $inpath/tempdir/*pattern "${inpath.baseName}.ome.zarr"
//             fi
//     elif [[ "${params.merge_files}" == "False" ]];
//         then
//             ${params.binpath}/run_conversion.py $inpath "${inpath.baseName}.ome.zarr"
//     fi
//     rm -rf "${inpath}/tempdir" &> /dev/null
//     rm -rf "${inpath}/*pattern" &> /dev/null
//     """
// }
//
//
//
