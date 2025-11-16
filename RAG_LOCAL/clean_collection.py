# clean_collection.py
import chromadb
from config import CHROMA_DIR

def main():
    print("🔗 Conectando a Chroma...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    print("🧹 Borrando colección 'docs'...")
    try:
        client.delete_collection("docs")
        print("✅ Colección eliminada.")
    except Exception as e:
        print(f"⚠ No se pudo eliminar (posiblemente ya no existe): {e}")

    print("📁 Creando colección vacía...")
    client.get_or_create_collection("docs")
    print("✨ Colección 'docs' creada y vacía.")

if __name__ == "__main__":
    main()
