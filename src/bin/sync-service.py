import os
import hashlib
import requests
import threading
import time
import signal
from datetime import datetime, timezone

from watchfiles import watch, Change

import psycopg2
import psycopg2.extras

def log(msg: str):
    print(msg, flush=True)

class ImmichDatabase:
    def __init__(self, host: str, database: str, user: str, password: str, port: int):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(host=self.host, database=self.database, user=self.user, password=self.password, port=self.port)
        self.conn.set_client_encoding('UTF8')

    def last_removed_asset(self, user_id: str) -> list[psycopg2.extras.RealDictRow]:
        """
        Retrieves the last removed asset for a given user.
        """

        if not self.conn or self.conn.closed != 0:
            self.connect()

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
        """
        Sets the 'file_removed' flag to 'true' for the specified asset ID in the 'assets_delete_audits' table.
        """

        if not self.conn or self.conn.closed != 0:
            self.connect()

        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE assets_delete_audits
                SET file_removed = 'true'
                WHERE asset_id = %s
            """, (asset_id,))
            self.conn.commit()

    def save_hash(self, user_id: str, asset_path: str, checksum: bytes) -> None:
        """
        Save the hash of the file in the database. If the file is already in the
        database the checksum is updated. The asset_path is the relative path
        to the user directory.
        """

        if not self.conn or self.conn.closed != 0:
            self.connect()

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
        if not self.conn or self.conn.closed != 0:
            self.connect()

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

    def get_asset_id_by_checksum(self, user_id: str, checksum: bytes) -> psycopg2.extras.RealDictRow | None:
        if not self.conn or self.conn.closed != 0:
            self.connect()

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT assets.id
                FROM assets
                INNER JOIN assets_filesync_lookup
                ON assets.checksum = assets_filesync_lookup.checksum
                WHERE assets_filesync_lookup.checksum = %s
                AND assets_filesync_lookup.user_id = %s
            """, (checksum, user_id))
            return cur.fetchone()

    def get_asset_created_at_by_path(self, user_id: str, asset_path: str) -> psycopg2.extras.RealDictRow | None:
        if not self.conn or self.conn.closed != 0:
            self.connect()

        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT assets."createdAt"
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
        for _ in range(10):
            r = requests.get(f"{self.host}/users/me", headers=self.headers)
            if r.status_code in [200]:
                return r.json()["id"]
            time.sleep(2)
        
        raise Exception(f"Failed to get user ID, status code {r.status_code}. Response: {r.text}")

    
    def delete_asset(self, asset_id: str) -> None:
        data = { "ids": [ asset_id ] }
        r = requests.delete(f"{self.host}/assets", headers=self.headers, json=data)
        if r.status_code not in [204]:
            raise Exception(f"Failed to delete asset {asset_id}, status code {r.status_code}. Response: {r.text}")

    def upload_asset(self, file_buffer, device_asset_id, file_created_at, file_modified_at):

        headers = {
            'Accept': 'application/json',
            'x-api-key': self.headers['x-api-key']
        }

        data = {
            "deviceAssetId": device_asset_id,
            "deviceId": "sync-service",
            "fileCreatedAt": file_created_at,
            "fileModifiedAt": file_modified_at,
            "isFavorite": "false",
        }

        response = requests.post(
            f"{self.host}/assets",
            headers=headers,
            data=data,
            files={"assetData": file_buffer}
        )

        return response

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

def import_asset(db: ImmichDatabase, api: ImmichAPI, base_path: str, asset_path: str) -> None:
    relative_path = os.path.relpath(asset_path, base_path)
    filename = os.path.basename(asset_path)
    stats = os.stat(asset_path)

    response = api.upload_asset(
        file_buffer=open(asset_path, "rb"),
        device_asset_id=f"{filename}-{stats.st_mtime}",
        file_created_at=datetime.fromtimestamp(stats.st_ctime),
        file_modified_at=datetime.fromtimestamp(stats.st_mtime)
    )

    if response.status_code not in [200, 201]:
        log(f"Failed to upload asset {asset_path}, status code {response.status_code}. Response: {response.text}")
    elif response.json().get("id") == None:
        log(f"Failed to upload asset {asset_path}, response: {response.text}")
    else:
        checksum = hash_file(asset_path)
        user_id = api.get_user_id()
        db.save_hash(user_id, relative_path, checksum)
        log(f"Hash {relative_path} and store in database for user {user_id})")

def delete_asset(db: ImmichDatabase, api: ImmichAPI, asset_path: str, base_path: str) -> None:
    relative_path = os.path.relpath(asset_path, base_path)
    user_id = api.get_user_id()
    asset = db.get_asset_id_by_path(user_id, relative_path)
    if asset:
        log(f"Asset {asset['id']} removed from database")
        api.delete_asset(asset["id"])
    else:
        log(f"Asset {relative_path} not found in database")

def get_file_age(db: ImmichDatabase, user_id: str, asset_path: str, user_path: str) -> int:
    """
    Calculate the age of the file in days. Returns 0 if the asset is not found in the database.
    """

    relative_path = os.path.relpath(asset_path, user_path)
    asset = db.get_asset_created_at_by_path(user_id, relative_path)
    if asset:
        return (datetime.now(timezone.utc) - asset["createdAt"]).days
    return 0

def import_watcher(event: threading.Event, db: ImmichDatabase, api: ImmichAPI, user_path: str) -> None:
    """
    Import watcher thread is responsible for scanning the user directory and
    updating the hash lookup table. It also imports assets that are missing.

    This thread is executed every day. It's intended for initial import,
    catch missing files and hash database updates.
    """

    log("Import watcher thread running...")
    while not event.is_set():
        for root, _, files in os.walk(user_path):
            for file in files:
                if ignored_paths(file):
                    continue

                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, user_path)
                user_id = api.get_user_id()
                checksum = hash_file(file_path)

                # Ignore missing files. This can happen if the file was deleted during execution.
                if not os.path.exists(file_path):
                    log(f"File {file_path} has disappeared, skipping")
                    continue

                #
                # Update hash lookup table
                #
                # Always do this, even if the asset is already in the database.
                # The heavy operation is the hash calculation, it's relatively
                # fast to check if update all records in the database.
                #
                # The idea is that the file may have been renamed or moved so this
                # is a way to keep the database up to date. There is a constraint
                # that prevents duplicate records.
                #
                db.save_hash(user_id, relative_path, checksum)

                #
                # Import assets that are missing in the database. This operation is
                # heavier and should be done only when needed.
                #
                if db.get_asset_id_by_checksum(api.get_user_id(), checksum) == None:
                    log(f"{file_path} not found in database, import asset to Immich")
                    import_asset(db, api, user_path, file_path)

        time.sleep(86400)

def file_watcher(event: threading.Event, db: ImmichDatabase, api: ImmichAPI, api_key: str, user_path: str) -> None:
    log("File watcher thread running...")
    delete_threshold =  int(os.environ["SYNC_DELETE_THRESHOLD"])
    for changes in watch(user_path, recursive=True, stop_event=event):
        for c_type, c_path in changes:

            if ignored_paths(c_path):
                continue

            if c_type == Change.added:
                log(f"{c_path} added, import asset to Immich")
                import_asset(db, api, user_path, c_path)
            elif c_type == Change.modified:
                log(f"{c_path} modified, re-import asset to Immich")
                import_asset(db, api, user_path, c_path)
            elif c_type == Change.deleted:
                user_id = api.get_user_id()
                file_age_days = get_file_age(db, user_id, c_path, user_path)

                if file_age_days < delete_threshold:
                    log(f"{c_path} deleted, mark asset as removed")
                    delete_asset(db, api, c_path, user_path)
                else:
                    log(f"{c_path} deleted, but it's older than {delete_threshold} days, keep asset in Immich")

def database_watcher(event: threading.Event, db: ImmichDatabase, api: ImmichAPI, user_path: str) -> None:
    log("Database watcher thread running...")
    user_id = api.get_user_id()
    while not event.is_set():

        try:
            last_rem_asset = db.last_removed_asset(user_id)
        except psycopg2.DatabaseError as e:
            log(f"Database error, retry in 10 seconds: {e}")
            time.sleep(10)
            continue

        for record in last_rem_asset:
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
    immich = ImmichAPI(f"{os.environ['IMMICH_SERVER_URL']}/api", api_key)
    snap_common = os.environ["SNAP_COMMON"]
    user_id = immich.get_user_id()
    user_path = f"{snap_common}/sync/{user_id}"

    log(f"Starting sync for user {user_id} at {user_path}")

    if not os.path.exists(user_path):
        os.makedirs(user_path)

    while len(os.listdir(user_path)) == 0:
        log(f"Waiting for files in {user_path}")
        time.sleep(10)

    stop_event = threading.Event()

    import_thread = threading.Thread(
        target=import_watcher,
        args=(stop_event, db, immich, user_path)
    )

    watch_thread = threading.Thread(
        target=file_watcher,
        args=(stop_event, db, immich, api_key, user_path)
    )

    database_thread = threading.Thread(
        target=database_watcher,
        args=(stop_event, db, immich, user_path)
    )

    import_thread.start()
    watch_thread.start()
    database_thread.start()

    signal.signal(signal.SIGTERM, lambda signum, frame: stop_event.set())

    while True:
        if not import_thread.is_alive():
            log("Critical: Thread import is not alive")
        if not watch_thread.is_alive():
            log("Critical: Thread watch is not alive")
        if not database_thread.is_alive():
            log("Critical: Thread database is not alive")
        time.sleep(10)

if __name__ == '__main__':
    main()
