import datetime
import argparse
import os
from typing import Any
from anki import collection, storage

from lib import ankicol


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="sync_command")

login_parser = subparsers.add_parser("login")
status_parser = subparsers.add_parser("status")

sync_parser = subparsers.add_parser("sync")

download_parser = subparsers.add_parser("download")
download_parser.add_argument("local_path", help="local path", type=str)

full_parser = subparsers.add_parser("full")
full_parser_subparsers = full_parser.add_subparsers(dest="sync_full_command")

full_parser_download = full_parser_subparsers.add_parser("download")
full_parser_upload = full_parser_subparsers.add_parser("upload")

full_parser_download.add_argument("backup_folder", help="backup folder", type=str)
full_parser_upload.add_argument("backup_folder", help="backup folder", type=str)


ENV_HKEY_KEY = "ANKI_HKEY"

STATUS = {
    0: "Not required",
    1: "Sync required",
    2: "Full sync required",
}


def get_status(acol: ankicol.AnkiCollection, hkey: str) -> collection.SyncStatus:
    auth = collection.SyncAuth(
        hkey=hkey,
        endpoint=None,
    )

    return acol.col.sync_status(auth)


# prints HKEY
def handle_login(acol: ankicol.AnkiCollection, args: Any) -> None:
    login = input("Login: ")
    password = input("Password: ")
    auth = acol.col.sync_login(login, password, None)
    print(auth.hkey)
    print(f"export {ENV_HKEY_KEY}={auth.hkey}")


def handle_status(acol: ankicol.AnkiCollection, args: Any) -> None:
    hkey = os.environ.get(ENV_HKEY_KEY)

    if hkey is None:
        print(f"{ENV_HKEY_KEY} not set")
        return

    s = get_status(acol, hkey)

    print(f"Status: {STATUS[s.required]}")
    print(f"Sync new endpoint: {s.new_endpoint}")


def handle_sync_sync(acol: ankicol.AnkiCollection, args: Any) -> None:
    hkey = os.environ.get(ENV_HKEY_KEY)
    if hkey is None:
        print(f"{ENV_HKEY_KEY} not set")
        return

    s = get_status(acol, hkey)

    auth = collection.SyncAuth(
        hkey=hkey,
        endpoint=s.new_endpoint,
    )

    if s.required == 0:
        print("Already synced")
        return

    if s.required == 1:
        print("Syncing...")
        res = acol.col.sync_collection(auth, False)
        print(res)
        return

    if s.required == 3:
        print("Full sync required.")
        return

        # acol.col.close_for_full_sync
        # acol.col.full_upload_or_download(auth, s, True)
        # acol.col.reopen()


def get_auth() -> collection.SyncAuth:
    hkey = os.environ.get(ENV_HKEY_KEY)
    if hkey is None:
        raise Exception(f"{ENV_HKEY_KEY} not set")

    return collection.SyncAuth(
        hkey=hkey,
        endpoint="https://sync19.ankiweb.net/",
    )


def handle_sync_full_download(acol: ankicol.AnkiCollection, args: Any) -> None:
    s = acol.col.sync_status(get_auth())

    if s.required != 2:
        print("Not a full sync")
        return

    succ = acol.backup(args.backup_folder)

    if not succ:
        print("Backup failed")
        return

    acol.col.close_for_full_sync()
    acol.col.full_upload_or_download(auth=get_auth(), upload=False, server_usn=None)
    acol.col.reopen(after_full_sync=True)


def handle_sync_full_upload(acol: ankicol.AnkiCollection, args: Any) -> None:

    s = acol.col.sync_status(get_auth())

    if s.required != 2:
        print("Not a full sync")
        return

    handle_sync_download(args.backup_folder)

    acol.col.close_for_full_sync()
    acol.col.full_upload_or_download(auth=get_auth(), upload=True, server_usn=None)
    acol.col.reopen(after_full_sync=True)


def handle_sync_download(local_path: str) -> None:
    """just download remote anki collection"""

    a = get_auth()

    # args.local_path
    # if it's folder, create a new collection with timestamp
    # else if it is unexisting, download to it
    is_dir = False
    if os.path.exists(local_path):
        if not os.path.isdir(local_path):
            raise Exception("local path exists")

        is_dir = True

    collection_path = local_path

    if is_dir:
        collection_path = os.path.join(local_path, f"remote-{timestamp()}.db")

    col = storage.Collection(collection_path)
    col.close_for_full_sync()
    col.full_upload_or_download(auth=a, upload=False, server_usn=None)
    col.reopen(after_full_sync=True)

    print(f"Remote collection downloaded to {collection_path}")


def handle_sync(acol: ankicol.AnkiCollection, args: Any) -> None:
    if args.sync_command is None:
        print("No command specified")
        return

    if args.sync_command == "login":
        return handle_login(acol, args)

    if args.sync_command == "status":
        return handle_status(acol, args)

    if args.sync_command == "sync":
        return handle_sync_sync(acol, args)

    if args.sync_command == "download":
        return handle_sync_download(args.local_path)

    if args.sync_command == "full":
        if args.sync_full_command == "upload":
            handle_sync_full_upload(acol, args)
        elif args.sync_full_command == "download":
            handle_sync_full_download(acol, args)
        else:
            print("No full sync action specified: upload or download")
