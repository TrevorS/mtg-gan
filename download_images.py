#!/usr/bin/env python

import sqlite3
from pathlib import Path
from sqlite3 import Connection

import requests

DATA_DIR = Path() / "data"
MTG_DB_URL = "https://mtgjson.com/api/v5/AllPrintings.sqlite"
MTG_DB_QUERY = "SELECT uuid, scryfallId, name from cards where setCode = ?"


def main(set_name="ZNR"):
    conn = prepare_db()

    download_images(conn, set_name)


def prepare_db() -> Connection:
    print("Checking for MTG JSON database...")

    db_path = DATA_DIR / "AllPrintings.sqlite"

    if db_path.exists():
        print(f"Found database: {db_path}.")

    else:
        print("Database not found, downloading...")

        DATA_DIR.mkdir(parents=True, exist_ok=True)
        download_file(MTG_DB_URL, DATA_DIR)

    return sqlite3.connect(db_path)


def download_images(conn: Connection, set_name: str):
    print("Downloading images...")

    set_path = DATA_DIR / "images" / set_name

    if set_path.exists():
        print(f"Found set images: {set_path}")

    else:
        print("Images not found, downloading...")
        set_path.mkdir(parents=True, exist_ok=True)

        for row in conn.cursor().execute(MTG_DB_QUERY, (set_name,)):
            uuid, scryfallId, name = row

            url = f"https://api.scryfall.com/cards/{scryfallId}?format=image&version=small"

            download_file(url, set_path, scryfallId + ".jpg")


def download_file(url: str, dst_dir: str, filename=None):
    if filename is None:
        filename = Path(url).name

    filename = Path(dst_dir).joinpath(filename)

    r = requests.get(url, stream=True)

    with open(filename, "wb") as file:
        for chunk in r.iter_content(chunk_size=128):
            file.write(chunk)


if __name__ == "__main__":
    main()
