#!/usr/bin/env nflow
nextflow.enable.dsl=2
import groovy.io.FileType

// Utility functions

def verify_axes(axes) {
    truth = true
    for (i in 0 .. axes.length() - 1) {
        if (axes[i] == "x") {
            truth = true
        }
        else if (axes[i] == "a") {
            truth = true
        }
        else if (axes[i] == ",") {
            truth = true
        }
        else if (axes == "auto") {
            truth = true
        }
        else {
            truth = false
        }
    }
    return truth
}

def verify_filenames_fromPath(directory, selby, rejby) {
	def files = []
	def dir = new File(directory)
// 	println(dir)

	dir.eachFileRecurse(FileType.FILES) { file ->
    	bool0 = (selby == "") || (file.toString().contains(selby))
    	bool1 = (rejby == "") || (!(file.toString().contains(rejby)))
		if (bool0 && bool1) {
			files << file
		}
// 		println((file.toString().contains(selby)))
// 		println(!(file.toString().contains(rejby)))
	}
	println(files)
	truth = true
	files.each {
		if (it.toString().contains(" ")) {
			truth = false
		}
	}
	return truth
}

def verify_filenames_fromCsv(fpath, selby, rejby, root_column, input_column) {
	def files = []
    ch_ = Channel.fromPath(fpath.toString()).
            splitCsv(header:true)
    if (params.root_column == 'auto'){
        ch0 = ch_.map { row-> file( row[params.input_column] ) }
    }
    else {
        ch0 = ch_.map { row-> file( row[root_column] + '/' + row[input_column] ) }
    }
    files = ch0.collect()
	truth = true
	files.each {
		if (it.toString().contains(" ")) {
			truth = false
		}
	}
	return truth
}

def verify_filenames_fromList(files, selby, rejby) {
	truth = true
	files.each {
		if (it.toString().contains(" ")) {
			truth = false
		}
	}
	return truth
}

def is_csv(fpath) {
    if (fpath instanceof File) {
        fpth = fpath.toString()
    }
    else if (fpath instanceof String) {
        fpth = fpath
    }
    else {
        println("'is_csv': fpath must be either of types File or String.")
        println( "fpath: " + fpath.toString() )
        return
    }
    return ( fpth.endsWith('.csv') || fpth.endsWith('.txt') )
}

def get_filenames_fromCSV(csvfile, selby, rejby) {
}

def get_filenames_fromList(files, selby, rejby) {
	def filtered = []
	files.each {
		if (it.toString().contains(selby) && !(it.toString().contains(rejby))) {
		    filtered << it
		}
	}
	return filtered
}

def parse_path_for_remote(path) {
    while ( path.startsWith(".") ) {
        path = path[1..-1];
    }

    while ( path.startsWith("/") ) {
        path = path[1..-1];
    }
    return path
}
