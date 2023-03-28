#!/usr/bin/env python3

import os
import time
import subprocess
import requests
import threading
import json
import hashlib
import re

SNAP = os.getenv("SNAP")
SNAP_COMMON = os.getenv("SNAP_COMMON")
IMMICH_SERVER_URL = os.getenv("IMMICH_SERVER_URL")

def upload(key, import_file):
    command = [f"{SNAP}/bin/immich-cli", "upload", "--key", key, "--yes", import_file]
    subprocess.run(" ".join(command), shell=True)

def hash_to_id(hash):
    command = [f"{SNAP}/bin/hash2id", hash]
    return subprocess.check_output(command).decode().strip()

def immich_server_ready():
    try:
        r = requests.get(f"{IMMICH_SERVER_URL}/server-info/ping")
    except:
        return False
    return r.status_code == 200

def get_keys():
    command = ["snapctl", "get", "sync"]
    return subprocess.check_output(command).decode().split()

def get_userid(key):
    url = f"{IMMICH_SERVER_URL}/user/me"
    headers = {
        "Accept": "application/json",
        "x-api-key": key
    }

    r = requests.get(url, headers=headers)
    return r.json()['id']

def delete_assets(key, asset_id):
    q = {"ids": [asset_id]}
    url = f"{IMMICH_SERVER_URL}/asset"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "x-api-key": key
    }
    r = requests.delete(url, headers=headers, data=json.dumps(q))
    if not r.status_code in [200, 201]:
        print(r.content)

def hash_file(path):
    command = ["sha1sum", path]
    return subprocess.check_output(command).decode().strip().split("  ")[0]

def load_hash_db(user_path):
    file = f"{user_path}/hash.db"
    if os.path.exists(file):
        try:
            return json.load(open(file))
        except json.decoder.JSONDecodeError:
            time.sleep(1)
            return load_hash_db(user_path)
    else:
        return {"file": {}, "hash": {}}

def write_hash_db(user_path, db):
    file = f"{user_path}/hash.db"
    with open(file, "w") as outfile:
        outfile.write(json.dumps(db))

def watch_created(user_path, key):
    command = ["fswatch", "--recursive", "--event", "Created", user_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    db = load_hash_db(user_path)

    for line in iter(process.stdout.readline, ""):
        file_path = line.decode().strip()
        is_dir = os.path.isdir(file_path)
        is_hidden = re.search(r'/\.[^/]+$', file_path)
        if os.path.exists(file_path) and not is_dir and not is_hidden:
            h = hash_file(file_path)
            db['hash'][h] = file_path
            db['file'][hashlib.sha256(line).hexdigest()] = h

            upload(key, file_path)
            write_hash_db(user_path, db)

def watch_removed(user_path, key):
    command = ["fswatch", "--recursive", "--event", "Removed", user_path]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)

    for line in iter(process.stdout.readline, ""):
        db = load_hash_db(user_path)
        filehash = hashlib.sha256(line).hexdigest()
        if filehash in db['file']:
            h = db['file'][filehash]
            id = hash_to_id(h)
            if id:
                delete_assets(key, id)
                print(f"Remove asset {id} from database", flush=True)

def watch_db():
    while True:
        time.sleep(10)
        remove_failed = False
        hash = subprocess.check_output([f"{SNAP}/bin/last-dbdel"]).decode().strip()
        if hash:
            db = load_hash_db(user_path)
            if hash in db['hash']:
                file_path = db['hash'][hash]
                if os.path.exists(file_path):
                    print(f"Remove {file_path}", flush=True)
                    try:
                        os.remove(file_path)
                    except PermissionError:
                        remove_failed = True

            if not remove_failed:
                subprocess.run(f"{SNAP}/bin/mark-dbdel {hash}", shell=True)

while not immich_server_ready():
    print("Server not ready", flush=True)
    time.sleep(10)

subprocess.run([f"{SNAP}/bin/modify-db"], shell=True)

for key in get_keys():
    user_id = get_userid(key)
    user_path = f"{SNAP_COMMON}/sync/{user_id}"
    t1 = threading.Thread(target=watch_created, args=(user_path, key))
    t1.start()
    t2 = threading.Thread(target=watch_removed, args=(user_path, key))
    t2.start()
    t3 = threading.Thread(target=watch_db)
    t3.start()
