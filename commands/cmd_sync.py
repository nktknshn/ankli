import argparse
import os
from typing import Any
from anki import collection

from lib import ankicol

parser = argparse.ArgumentParser(add_help=False)
subparsers = parser.add_subparsers(dest="sync_command")
login_parser = subparsers.add_parser("login")
status_parser = subparsers.add_parser("status")
sync_parser = subparsers.add_parser("sync")

ENV_HKEY_KEY = "ANKI_HKEY"


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

    print(f"Sync required: {s.required}")
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
