#!/usr/bin/env nflow
nextflow.enable.dsl=2

// Note that you can move the parameterise python scripts as a beforeScript directive

// Conversion processes

process Convert_EachFile2SeparateOMETIFF {
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
    batchconvert_cli.sh $inpath "${inpath.baseName}.ome.tiff"
    """
}

process Convert_Concatenate2SingleOMETIFF {
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
    if [[ "${params.concatenation_order}" == "auto" ]];
        then
            batchconvert_cli.sh "${inpath}/${pattern_file}" "${pattern_file.baseName}.ome.tiff"
    elif ! [[ "${params.concatenation_order}" == "auto" ]];
        then
            batchconvert_cli.sh "${inpath}/tempdir/${pattern_file}" "${pattern_file.baseName}.ome.tiff"
    fi
    # rm -rf ${inpath}/tempdir &> /dev/null
    # rm -rf ${inpath}/*pattern &> /dev/null
    """
}

process Convert_EachFile2SeparateOMEZARR {
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
    batchconvert_cli.sh $inpath "${inpath.baseName}.ome.zarr"
    """
}

process Convert_Concatenate2SingleOMEZARR{
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
    if [[ "${params.concatenation_order}" == "auto" ]];
        then
            batchconvert_cli.sh "${inpath}/${pattern_file}" "${pattern_file.baseName}.ome.zarr"
    elif ! [[ "${params.concatenation_order}" == "auto" ]];
        then
            batchconvert_cli.sh "${inpath}/tempdir/${pattern_file}" "${pattern_file.baseName}.ome.zarr"
    fi
    # rm -rf ${inpath}/tempdir &> /dev/null
    # rm -rf ${inpath}/*pattern &> /dev/null
    """
}

// Transfer processes:

process Transfer_Local2S3Storage {
    input:
        path local
    output:
        path "./transfer_report.txt", emit: tfr
    script:
    """
    localname="\$(basename $local)" && \
    mc alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    if [ -f $local ];then
        mc cp $local "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${params.out_path}"/"\$localname";
    elif [ -d $local ];then
        mc mirror $local "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${params.out_path}"/"\$localname";
    fi
    echo "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${params.out_path}"/$local > "./transfer_report.txt";
    """
}


process Transfer_S3Storage2Local {
    input:
        val source
    output:
        path "transferred/${source}"
    script:
    """
    mc alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    mc mirror "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${source}" "transferred/${source}";
    """
}


process Transfer_Local2PrivateBiostudies {
    input:
        path local
    output:
        path "./transfer_report.txt", emit: tfr
    script:
    """
    ascp -P33001 -l 500M -k 2 -i $BIA_SSH_KEY -d $local bsaspera_w@hx-fasp-1.ebi.ac.uk:${params.BIA_REMOTE}/${params.out_path};
    echo "${params.BIA_REMOTE}"/"${params.out_path}" > "./transfer_report.txt";
    """
}

process Transfer_PrivateBiostudies2Local {
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


// Other utilities

process createPatternFile1 {
    input:
        path inpath
    output:
        path "${inpath}/*"
    script:
    """
    if [[ "${params.pattern}" == '' ]];then
        create_hyperstack ${inpath}
    else
        create_hyperstack --select_by ${params.pattern} ${inpath}
    fi
    """
}


process createPatternFile2 {
    input:
        path inpath
    output:
        path "${inpath}/tempdir/*"
    script:
    """
    if [[ "${params.pattern}" == '' ]];then
        create_hyperstack --concatenation_order ${params.concatenation_order} ${inpath}
    else
        create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} ${inpath}
    fi
    """
}


















// EXPERIMENTAL PROCESSES THAT ARE CURRENTLY NOT NEEDED
process cleanup {
    input:
        path inpath
    script:
    """
    rm -rf "${inpath}/tempdir" &> /dev/null
    rm -rf "${inpath}/*pattern" &> /dev/null
    """
}



process mirror2local {
    input:
        val source
    output:
        path "transferred"
    script:
    """
    mc alias set "${params.S3REMOTE}" "${params.S3ENDPOINT}" "${params.S3ACCESS}" "${params.S3SECRET}";
    mc mirror "${params.S3REMOTE}"/"${params.S3BUCKET}"/"${source}" "transferred";
    """
}


process stageLocal {
    input:
        path filepath
    output:
        path "${filepath.baseName}"
    """
    """
}

process stageLocalPublish {
    if ("${params.dest_type}"=="local") {
        publishDir(
            path: "${params.out_path}",
            mode: 'copy'
        )
    }
    input:
        path filepath
    output:
        path "${filepath.baseName}"
    """
    """
}


process bioformats2raw_experimental {
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
    if [[ "${params.merge_files}" == "True" ]];
        then
            create_hyperstack --concatenation_order ${params.concatenation_order} --select_by ${params.pattern} ${inpath};
            if [[ "${params.concatenation_order}" == "auto" ]];
                then
                    batchconvert_cli.sh $inpath/*pattern "${inpath.baseName}.ome.zarr"
            elif ! [[ "${params.concatenation_order}" == "auto" ]];
                then
                    batchconvert_cli.sh $inpath/tempdir/*pattern "${inpath.baseName}.ome.zarr"
            fi
    elif [[ "${params.merge_files}" == "False" ]];
        then
            batchconvert_cli.sh $inpath "${inpath.baseName}.ome.zarr"
    fi
    rm -rf "${inpath}/tempdir" &> /dev/null
    rm -rf "${inpath}/*pattern" &> /dev/null
    """
}



