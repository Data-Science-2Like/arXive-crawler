import os
import tarfile
import tempfile
import shutil
import subprocess
from os import path
from pathlib import Path

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
    encodings = ['utf-8', 'ascii']  # add more
    for e in encodings:
        try:
            with open(file, mode="r", encoding="utf-8") as f:
                if str in f.read():
                    return True
                else:
                    return False
        except UnicodeDecodeError:
            print('got unicode error with %s , trying different encoding' % e)
            continue
        else:
            break
    return False


def move_file(source, dest, override=False):
    if not path.exists(source) or (path.exists(dest) and not override):
        return
    dest_drive = os.path.splitdrive(dest)
    source_drive = os.path.splitdrive(source)
    if dest_drive == source_drive:
        os.rename(source, dest)
    else:
        # when output directory is on a different disk than the temp directory we need to use another function
        # https://python.omics.wiki/file-operations/file-commands/os-rename-vs-shutil-move
        if os.path.exists(os.path.join(os.path.dirname(dest), os.path.basename(source))):
            os.remove(os.path.join(os.path.dirname(dest), os.path.basename(source)))
        shutil.move(source, os.path.dirname(dest))
        os.rename(os.path.join(os.path.dirname(dest), os.path.basename(source)), dest)

def change_ext(source, ext):
    p = Path(source)
    p.rename(p.with_suffix(ext))

def extractLatex(source, dest, debug, bibtex, start):
    # check if destination folder exists else create
    if not path.exists(dest):
        os.mkdir(dest)

    tmpWorkingDir = tempfile.mkdtemp()

    # we need to set the enviroment variable here for the perl script to use this as
    # a working directory
    os.environ["TEXINPUTS"] = tmpWorkingDir
    skipping = False
    for filename in os.listdir(source):
        if filename.endswith("tar.gz"):
            idStr = filename.split(".")[0]
            if start > int(idStr):
                if not skipping:
                    print("Skipping entries")
                    skipping = True
                continue
            skipping = False
            print("Started extracting paper ", idStr)
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
            bib_found = False
            for candidate in os.listdir(tmpWorkingDir):
                if candidate.endswith(".tex") and check_if_main(os.path.join(tmpWorkingDir, candidate)):
                    mainFile = os.path.join(tmpWorkingDir, candidate)
                    break

                # if bibtex option is set also export bibtex file
                if candidate.endswith(".bib") and bibtex:
                    bib_found = True
                    idStr = filename.split(".")[0] + ".bib"
                    move_file(os.path.join(tmpWorkingDir, candidate), os.path.join(dest, idStr))
                if candidate.endswith(".bbl") and bibtex:
                    bib_found = True
                    idStr = filename.split(".")[0] + ".bbl"
                    move_file(os.path.join(tmpWorkingDir, candidate), os.path.join(dest, idStr))

            if bibtex and not bib_found:
                print(f"Couldn't find bibliography file for {filename}")

            if mainFile == "":
                print(f"Couldn't find main latex file, skipping {filename}")
                continue
            try:
                # nome execute the perl script
                # mainStr = f"'{mainFile}'"
                destPath = os.path.join(tmpWorkingDir, "outputExpander.tex")
                # destStr = f" -o {destPath}"
                # scriptPath = os.path.join(os.getcwd(), "latexpand.pl")
                subprocess.call(["perl", "latexpand.pl", mainFile, "-o", destPath],timeout=90)
            except TimeoutError as e:
                print("Timeout occured at ", str(idStr))
                change_ext(filename,".tar.gz.wtf")
                continue
            except Exception as e:
                print(e)

            # now move file to output directory
            idStr = filename.split(".")[0] + ".tex"
            move_file(os.path.join(tmpWorkingDir, "outputExpander.tex"), os.path.join(dest, idStr))

            # source latexpand: https://gitlab.com/latexpand/latexpand/-/blob/master/latexpand
    # remove the working temp directory after being done
    shutil.rmtree(tmpWorkingDir)
