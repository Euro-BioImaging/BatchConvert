import os, json, subprocess, sys
from subprocess import PIPE

if __name__ == "__main__":
    scriptpath = os.path.dirname(os.path.realpath(__file__))
    cmd = [os.path.join(scriptpath, "batchconvert"), *sys.argv[1:]]
    result = subprocess.run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    if len(result.stderr) == 0:
        print(result.stdout)
    else:
        print(result.stderr)
