import os, json, subprocess, sys
from subprocess import PIPE
import shutil

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    homepath = os.environ.get('HOMEPATH')
    temppath = os.environ.get('TEMPPATH')
    parampath = os.environ.get('PARAMPATH')
    binpath = os.environ.get('BINPATH')
    configpath = os.environ.get('CONFIGPATH')
    paramsource = os.path.join(scriptpath, '..', 'params')
    paramfnames = os.listdir(paramsource)
    paramfpaths = [os.path.join(paramsource, item) for item in paramfnames]
    configsource = os.path.join(scriptpath, '..', 'configs')
    configfnames = os.listdir(configsource)
    configfpaths = [os.path.join(configsource, item) for item in configfnames]

    if not os.path.exists(parampath):
        os.makedirs(parampath)
    if not os.path.exists(temppath):
        os.makedirs(temppath)
    if not os.path.exists(homepath):
        os.makedirs(homepath)
    if not os.path.exists(binpath):
        os.makedirs(binpath)
    if not os.path.exists(configpath):
        os.makedirs(configpath)

    for fpath, fname in zip(paramfpaths, paramfnames):
        destpath = os.path.join(parampath, fname)
        if not os.path.exists(destpath):
            shutil.copy(fpath, destpath)

    for fpath, fname in zip(configfpaths, configfnames):
        destpath = os.path.join(configpath, fname)
        if not os.path.exists(destpath):
            shutil.copy(fpath, destpath)

    cmd = [os.path.join(scriptpath, "batchconvert"), *sys.argv[1:]]
    interactive_commands = ['configure_s3_remote', 'configure_ometiff', 'configure_omezarr', 'configure_slurm']
    if len(cmd) == 2 and cmd[1] in interactive_commands:
        proc = subprocess.Popen(cmd, universal_newlines=True)
        _ = proc.communicate()
    else:
        proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, error = proc.communicate()
        if len(error) == 0:
            with open(os.path.join(temppath, '.stdout'), 'w') as writer:
                writer.write(out)
        else:
            with open(os.path.join(temppath, '.stderr'), 'w') as writer:
                writer.write(error)


