import datetime
import argparse
import os
from typing import Any
from anki import collection, storage

from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="sync_command")
login_parser = subparsers.add_parser("login")
status_parser = subparsers.add_parser("status")
sync_parser = subparsers.add_parser("sync")
download_parser = subparsers.add_parser("download")

ENV_HKEY_KEY = "ANKI_HKEY"

STATUS = {
    0: "Not required",
    1: "Sync required",
    2: "Full sync required",
}


def get_status(acol: ankicol.AnkiCollection, hkey: str) -> collection.SyncStatus:
    auth = collection.SyncAuth(
        hkey=hkey,
        endpoint="https://sync.ankiweb.net/",
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


download_parser.add_argument("local_path", help="local path", type=str)


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def handle_sync_download(acol: ankicol.AnkiCollection, args: Any) -> None:
    """just download remote anki collection"""
    hkey = os.environ.get(ENV_HKEY_KEY)

    if hkey is None:
        print(f"{ENV_HKEY_KEY} not set")
        return

    # args.local_path
    # if it's folder, create a new collection with timestamp
    # else if it is unexisting, download to it
    is_dir = False
    if os.path.exists(args.local_path):
        if not os.path.isdir(args.local_path):
            print("local path exists")
            return

        is_dir = True

    collection_path = args.local_path

    if is_dir:
        collection_path = os.path.join(args.local_path, f"remote-{timestamp()}.db")

    col = storage.Collection(collection_path)

    a = collection.SyncAuth(hkey=hkey, endpoint="https://sync19.ankiweb.net/")

    s = col.sync_status(a)

    if s.required != 2:
        print("Not a full sync")
        return

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
        return handle_sync_download(acol, args)

    if args.sync_command == "full":
        if args.sync_full_command == "upload":
            pass
        elif args.sync_full_command == "download":
            pass
