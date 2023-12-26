#!/usr/bin/env python3

import argparse
import os
import sys
import yaml
import os
import glob
import shutil
import hashlib

def ftxt(text, color):
    colors = {
        "red": "\033[91m",
        "yellow": "\033[93m",
        "bold": "\033[1m",
        "reset": "\033[0m"
    }
    return f"{colors[color]}{text}{colors['reset']}"


def ftxt_b(text):
    return ftxt(text, "bold")


def ftxt_r(text):
    return ftxt(text, "red")


def find_files(directory, filename):
    matches = []
    for root, _, files in os.walk(directory):
        if filename in files:
            matches.append(os.path.join(root, filename))
    return matches


def find_dependency(name):
    print(ftxt_b(f">>> Finding dependency {name}..."))
    for scy in find_files(".", "snapcraft.yaml"):
        with open(scy, "r") as stream:
            try:
                snapcraft = yaml.load(stream, Loader=yaml.FullLoader)
                if snapcraft.get("name") == name:
                    return os.path.dirname(scy)
            except yaml.YAMLError as exc:
                print(exc)
    return None


def hash_file(path: str) -> str:
    file_hash = hashlib.sha1()
    with open(path, "rb") as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.hexdigest()


def build(dependency, root_path):
    print(ftxt_b(f">>> Building dependency {dependency}..."))

    os.system(f"cd {root_path} && snapcraft")
    os.system(f"multipass stop snapcraft-{dependency}")

    for file in glob.glob(os.path.join(root_path, "*.snap")):
        new_name = os.path.join(root_path, f"{dependency}.snap")
        os.rename(file, new_name)


def stage(dependency, root_path, workdir):
    print(ftxt_b(f">>> Staging {dependency}..."))
    
    tmpdir = os.path.join(root_path, "temp")
    shutil.rmtree(tmpdir, ignore_errors=True)
    os.makedirs(tmpdir, exist_ok=True)
    os.system(f"unsquashfs -d {tmpdir} {root_path}/{dependency}.snap")
    shutil.rmtree(os.path.join(tmpdir, 'meta'), ignore_errors=True)
    shutil.rmtree(os.path.join(tmpdir, 'snap'), ignore_errors=True)

    filelist = []
    for root, _, files in os.walk(tmpdir):
        for file in files:
            filelist.append(os.path.relpath(os.path.join(root, file), tmpdir))

    size = round(sum(os.path.getsize(os.path.join(tmpdir, f)) for f in filelist) / 1024 / 1024)
    print(f"Stats: {len(filelist)} files, filesize: {size} MB")
    print(f"Copied files: ", end="", flush=True)

    for file in filelist:
        if os.path.isfile(f"{workdir}/{file}"):
            file_hash_new =  hash_file(f"{tmpdir}/{file}")
            file_hash_existing =  hash_file(f"{workdir}/{file}")
            if file_hash_new == file_hash_existing:
                print(f"-", end="", flush=True)
                continue
            else:
                print(f"E")
                print(ftxt_r(f"[Error] A different version of {file} already exists in workdir!"))
                print(f"[!] {dependency}: {file_hash_new}")
                print(f"[!] workdir: {file_hash_existing}")
                sys.exit(1)
        else:
            print(f".", end="", flush=True)
            os.makedirs(os.path.dirname(f"{workdir}/{file}"), exist_ok=True)
            shutil.copy2(f"{tmpdir}/{file}", f"{workdir}/{file}", follow_symlinks=False)
    print()

    print(ftxt_b(f">>> Clean temporay folder for {dependency}..."))
    shutil.rmtree(tmpdir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build dependency")
    parser.add_argument("-b", "--build", metavar="dependency", help="Build dependency", required=True)
    parser.add_argument("-w", "--workdir", metavar="workdir", help="Path to the workdir", required=True)
    args = parser.parse_args()

    if args.build:
        root_path = find_dependency(args.build)
        if root_path is None:
            print(ftxt(f"Dependency {args.build} not found", "red"))
            exit(1)

        build(args.build, root_path)
        stage(args.build, root_path, args.workdir)
