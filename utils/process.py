import sys
import os
import logging
import subprocess
import shutil

def run(executable, args, working_dir):
    # find executable
    executable_full_path = shutil.which(executable)
    # add executable full path as argv[0]
    args.insert(0, executable_full_path)
    # run subprocess
    p = subprocess.Popen(args, executable=executable_full_path, cwd=working_dir)
    # get output
    (stdout, stderr) = p.communicate()
    return p.returncode
