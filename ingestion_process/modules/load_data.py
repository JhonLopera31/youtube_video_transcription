import json
import os

import psycopg2


def _get_db_credentials() -> dict:
    """
    Retrieve database connection credentials from the environment.
    :return: Dictionary containing connection credentials.
    """
    credentials = os.environ.get("POSTGRES_CREDENTIALS")

    return {
        "host": credentials[0],
        "username": credentials[1],
        "password": credentials[2],
        "database": credentials[3],
        "port": credentials[4],
    }

import psycopg2
import json

def load_to_postgres(json_file_path: str):
    """
    Loads video transcript data from a JSON file into a PostgreSQL database.

    Args:
        json_file_path (str): The file path to the JSON file containing video transcript data.

    The JSON file should have a list of dictionaries with the following structure:
    [
        {"video_id": "abc123", "text": "Transcript content..."},
        {"video_id": "def456", "text": "Another transcript..."}
    ]

    """
    conn = psycopg2.connect(**_get_db_credentials())
    cursor = conn.cursor()

    with open(json_file_path, "r") as f:
        data = json.load(f)

    for item in data:
        cursor.execute(
            "INSERT INTO videos (video_id, transcript) VALUES (%s, %s)",
            (item["video_id"], item["text"])
        )

    conn.commit()
    cursor.close()
    conn.close()
