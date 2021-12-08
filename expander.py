import os
import tarfile
import tempfile
import shutil
import subprocess
from os import path

def clearFolder(folder):
    # shamelessly copied from https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def texFiles(members):
    # generator function to select files to export taken from https://docs.python.org/3/library/tarfile.html
    for tarinfo in members:
        # assuming we are only interested in the .tex files
        if tarinfo.name.endswith("tex"):
            yield tarinfo

def check_if_main(file):
    if os.path.isdir(file):
        return False
    str = "\\begin{document}"
    with open(file) as f:
        if str in f.read():
            return True
        else:
            return False

def extractLatex(source,dest):

    #check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    tmpWorkingDir = tempfile.mkdtemp()

    # we need to set the enviroment variable here for the perl script to use this as
    # a working directory
    os.environ["TEXINPUTS"] = tmpWorkingDir

    for filename in os.listdir(source):
        if filename.endswith("tar.gz"):

            clearFolder(tmpWorkingDir)
            # print(os.path.join(source, filename))
            try:
                tar = tarfile.open(os.path.join(source, filename))
                # tar.extractall(tmpWorkingDir,members=texFiles(tar))
                tar.extractall(tmpWorkingDir)
            except Exception:
                continue

            # find main file
            mainFile = str()
            for candidate in os.listdir(tmpWorkingDir):
                try:
                    if check_if_main(os.path.join(tmpWorkingDir, candidate)):
                        mainFile = os.path.join(tmpWorkingDir, candidate)
                        break
                except UnicodeDecodeError:
                    # skipping non text file
                    continue

            try:
                # nome execute the perl script
                # mainStr = f"'{mainFile}'"
                destPath = os.path.join(tmpWorkingDir, "outputExpander.tex")
                # destStr = f" -o {destPath}"
                # scriptPath = os.path.join(os.getcwd(), "latexpand.pl")
                subprocess.call(["perl", "latexpand.pl", mainFile, "-o", destPath])
            except Exception as e:
                print(e)

            # now move file to output directory
            idStr = filename.split(".")[0] + ".tex"
            if path.exists(os.path.join(tmpWorkingDir, "outputExpander.tex")) and not path.exists(os.path.join(dest, idStr)) :
                os.rename(os.path.join(tmpWorkingDir, "outputExpander.tex"), os.path.join(dest, idStr))

            # source latexpand: https://gitlab.com/latexpand/latexpand/-/blob/master/latexpand
    # remove the working temp directory after being done
    shutil.rmtree(tmpWorkingDir)