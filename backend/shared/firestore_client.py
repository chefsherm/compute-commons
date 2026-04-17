import os
from google.cloud import firestore

def get_firestore_client():
    # Use emulator if host is provided in environment
    if os.getenv("FIRESTORE_EMULATOR_HOST"):
        return firestore.Client(project="compute-commons", credentials=None)

    # Fallback for local development/testing if no credentials provided
    try:
        return firestore.Client()
    except Exception:
        # In a real environment, we'd have credentials.
        # For this task, we might be running in a sandbox without them.
        return None
