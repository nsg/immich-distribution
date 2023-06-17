import os
import hashlib
import subprocess
import requests
import threading
import time
import signal

from watchfiles import watch, Change

import psycopg2
import psycopg2.extras

def log(msg: str):
    print(msg, flush=True)

class ImmichDatabase:
    def __init__(self, host: str, database: str, user: str, password: str, port: int):
        self.conn = psycopg2.connect(host=host, database=database, user=user, password=password, port=port)
        self.conn.set_client_encoding('UTF8')

    def last_removed_asset(self, user_id: str) -> list[psycopg2.extras.RealDictRow]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    assets_filesync_lookup.asset_path,
                    assets_delete_audits.asset_id
                FROM assets_delete_audits
                INNER JOIN assets_filesync_lookup
                ON assets_delete_audits.checksum = assets_filesync_lookup.checksum
                AND assets_delete_audits.user_id = assets_filesync_lookup.user_id
                WHERE assets_filesync_lookup.user_id = %s
                AND assets_delete_audits.file_removed = 'false'
                ORDER BY changed_on desc
                LIMIT 1
            """, (user_id,))

            return cur.fetchall()

    def set_asset_removed(self, asset_id: str) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE assets_delete_audits
                SET file_removed = 'true'
                WHERE asset_id = %s
            """, (asset_id,))
            self.conn.commit()

    def save_hash(self, user_id: str, asset_path: str, checksum: bytes) -> None:
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO
                assets_filesync_lookup(user_id, asset_path, checksum)
                VALUES(%s, %s, %s)
                ON CONFLICT (user_id, asset_path) DO
                    UPDATE SET checksum = %s
                    WHERE assets_filesync_lookup.asset_path = %s
                    AND assets_filesync_lookup.user_id = %s;
            """,
            (user_id, asset_path, checksum,
             checksum, asset_path, user_id))
            self.conn.commit()

    def get_asset_id_by_path(self, user_id: str, asset_path: str) -> psycopg2.extras.RealDictRow | None:
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT assets.id
                FROM assets
                INNER JOIN assets_filesync_lookup
                ON assets.checksum = assets_filesync_lookup.checksum
                WHERE assets_filesync_lookup.asset_path = %s
                AND assets_filesync_lookup.user_id = %s
            """, (asset_path, user_id))
            return cur.fetchone()

    def close(self):
        self.conn.commit()
        self.conn.close()

class ImmichAPI:
    def __init__(self, host: str, api_key: str):
        self.host = host
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-api-key": api_key
        }

    def get_user_id(self) -> str:
        r = requests.get(f"{self.host}/user/me", headers=self.headers)
        return r.json()["id"]
    
    def delete_asset(self, asset_id: str) -> dict:
        data = { "ids": [ asset_id ] }
        r = requests.delete(f"{self.host}/asset", headers=self.headers, json=data)
        return r.json()

def hash_file(path: str) -> bytes:
    file_hash = hashlib.sha1()
    with open(path, "rb") as f:
        fb = f.read(2048)
        while len(fb) > 0:
            file_hash.update(fb)
            fb = f.read(2048)
    return file_hash.digest()

def ignored_paths(path: str) -> bool:
    if os.path.basename(path).startswith("."):
        return True

    if os.path.isdir(path):
        return True
    
    return False

def hash_all_files(db: ImmichDatabase, user_id: str, path: str) -> None:
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, path)
            db.save_hash(user_id, relative_path, hash_file(file_path))
            log(f"Hash for {file_path} stored in database")

def import_asset(db: ImmichDatabase, api: ImmichAPI, key: str, base_path: str, asset_path: str) -> None:
    snap_path = os.getenv("SNAP")
    relative_path = os.path.relpath(asset_path, base_path)
    import_command = [
        f"{snap_path}/bin/immich-cli", "upload",
        "--server", os.getenv("IMMICH_SERVER_ADDRESS"),
        "--key", key,
        "--yes",
        asset_path
    ]

    if snap_path:
        result = subprocess.run(import_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        result = subprocess.CompletedProcess([], 0)
        log(f"MOC: {import_command}")

    if result and result.returncode != 0:
        log(f"Error: Failed to import {asset_path}")
        log(f"CLI (stdout): {result.stdout.decode('utf-8')}")
        log(f"CLI (stderr): {result.stderr.decode('utf-8')}")
    else:
        checksum = hash_file(asset_path)
        user_id = api.get_user_id()
        db.save_hash(user_id, relative_path, checksum)
        log(f"{relative_path} hash {checksum.hex()} user {user_id})")

def delete_asset(db: ImmichDatabase, api: ImmichAPI, asset_path: str, base_path: str) -> None:
    relative_path = os.path.relpath(asset_path, base_path)
    user_id = api.get_user_id()
    asset = db.get_asset_id_by_path(user_id, relative_path)
    if asset:
        print(f"Asset {asset['id']} removed from database")
        api.delete_asset(asset["id"])
    else:
        print(f"ERROR: Asset {relative_path} not found in database")

def file_watcher(event: threading.Event, db: ImmichDatabase, api: ImmichAPI, api_key: str, user_path: str) -> None:
    log("File watcher thread running...")
    for changes in watch(user_path, recursive=True, stop_event=event):
        for c_type, c_path in changes:

            if ignored_paths(c_path):
                continue

            if c_type == Change.added:
                log(f"{c_path} added, import asset to Immich")
                import_asset(db, api, api_key, user_path, c_path)
            elif c_type == Change.modified:
                log(f"{c_path} modified, re-import asset to Immich")
                import_asset(db, api, api_key, user_path, c_path)
            elif c_type == Change.deleted:
                log(f"{c_path} deleted, mark asset as removed")
                delete_asset(db, api, c_path, user_path)

def database_watcher(event: threading.Event, db: ImmichDatabase, api: ImmichAPI, user_path: str) -> None:
    log("Database watcher thread running...")
    user_id = api.get_user_id()
    while not event.is_set():
        for record in db.last_removed_asset(user_id):
            asset_id = record['asset_id']
            asset_path = record['asset_path']
            full_path = f"{user_path}/{asset_path}"
            if os.path.exists(full_path):
                log(f"Remove asset {asset_id} user {user_id} path {asset_path}")
                os.remove(full_path)
            else:
                log(f"Asset {asset_id} user {user_id} path {asset_path} already removed")
            log(f"Mark asset {asset_id} as removed")
            db.set_asset_removed(asset_id)
        time.sleep(5)

def main():
    db = ImmichDatabase(
        host=os.environ["DB_HOSTNAME"],
        database=os.environ["DB_DATABASE_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"],
        port=5432
    )

    api_key = os.environ["IMMICH_API_KEY"]
    immich = ImmichAPI(os.environ["IMMICH_SERVER_URL"], api_key)
    snap_common = os.environ["SNAP_COMMON"]
    user_id = immich.get_user_id()
    user_path = f"{snap_common}/sync/{user_id}"

    log(f"Starting sync for user {user_id} at {user_path}")

    log(f"Initial file hash import of all files in {user_path}")
    hash_all_files(db, user_id, user_path)

    stop_event = threading.Event()

    watch_thread = threading.Thread(
        target=file_watcher,
        args=(stop_event, db, immich, api_key, user_path)
    )

    database_thread = threading.Thread(
        target=database_watcher,
        args=(stop_event, db, immich, user_path)
    )

    watch_thread.start()
    database_thread.start()

    signal.signal(signal.SIGTERM, lambda signum, frame: stop_event.set())

    while True:
        print("Running thread watch")

        if not watch_thread.is_alive():
            print("Critical: Thread watch is not alive")
        if not database_thread.is_alive():
            print("Critical: Thread database is not alive")
        time.sleep(10)

if __name__ == '__main__':
    main()
