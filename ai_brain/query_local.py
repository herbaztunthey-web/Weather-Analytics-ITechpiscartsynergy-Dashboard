from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


def ask_the_brain():
    VECTOR_DB_DIR = "ai_brain/vector_store"

    # We use the same local model that we used to train
    print("🧠 Waking up the Local Data Brain...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Connect to the memory we just created
    db = Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)

    # Interactive loop
    while True:
        query = input("\nAsk about your weather history (or type 'exit'): ")
        if query.lower() == 'exit':
            break

        # Search the memory for the 3 most relevant events
        results = db.similarity_search(query, k=3)

        print("\n--- 🤖 AI Memory Retrieval ---")
        if not results:
            print("I don't remember anything about that.")
        for i, res in enumerate(results):
            print(f"{i+1}. {res.page_content}")


if __name__ == "__main__":
    ask_the_brain()
