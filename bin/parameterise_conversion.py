import os, json, subprocess, sys
from subprocess import PIPE

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    cmd = [os.path.join(scriptpath, "batchconvert"), *sys.argv[1:]]
    interactive_commands = ['configure_s3_remote', 'configure_ometiff', 'configure_omezarr', 'configure_slurm']
    if len(cmd) > 1 and cmd[1] in interactive_commands:
        proc = subprocess.Popen(cmd, universal_newlines=True)
        _ = proc.communicate()
    else:
        proc = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        out, error = proc.communicate()
        if len(error) == 0:
            with open(os.path.join(scriptpath, '.stdout'), 'w') as writer:
                writer.write(out)
        else:
            with open(os.path.join(scriptpath, '.stderr'), 'w') as writer:
                writer.write(error)