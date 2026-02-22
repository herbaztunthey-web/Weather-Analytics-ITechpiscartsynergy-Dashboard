import sqlite3
import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Configuration
DB_PATH = "final_weather.db"
VECTOR_DB_DIR = "ai_brain/vector_store"


def train_brain():
    if not os.path.exists(DB_PATH):
        print("Error: final_weather.db not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Reading from your 'history' table
    print("Reading weather history...")
    cursor.execute("SELECT city, temp, timestamp, unit FROM history")
    rows = cursor.fetchall()

    documents = []
    for row in rows:
        # CLEANING LOGIC: Fix 'None' or 'metric' display issues
        raw_unit = row[3]
        unit_label = "°C" if raw_unit is None or raw_unit == "metric" else raw_unit

        text_memory = f"In {row[0]}, the temperature was {row[1]}{unit_label} at {row[2]}."
        doc = Document(page_content=text_memory, metadata={
                       "city": row[0], "time": row[2]})
        documents.append(doc)

    if not documents:
        print("No data found in history table.")
        return

    # 1. Initialize LOCAL AI Memory
    print("Loading local AI model and indexing data...")
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    # 2. Store in Vector Database (Overwrites old messy data with clean data)
    vector_db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR
    )

    print(
        f"✅ Success! Local Data Brain now remembers {len(documents)} cleaned weather events.")
    conn.close()


if __name__ == "__main__":
    train_brain()
