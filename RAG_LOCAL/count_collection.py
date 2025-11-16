# count_collection.py
import chromadb
from config import CHROMA_DIR

def main():
    print("🔗 Conectando a Chroma...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    col = client.get_or_create_collection("docs")

    print(f"📊 Total de documentos/chunks en la colección: {col.count()}")

if __name__ == "__main__":
    main()
