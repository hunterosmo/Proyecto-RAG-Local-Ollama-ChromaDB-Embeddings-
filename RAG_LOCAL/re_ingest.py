# re_ingest.py
import subprocess
import sys
import chromadb
from config import CHROMA_DIR

def main():
    print("🔗 Conectando a Chroma...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    print("🧹 Eliminando colección 'docs'...")
    try:
        client.delete_collection("docs")
        print("✅ Colección eliminada.")
    except Exception as e:
        print(f"⚠ No se pudo eliminar (posiblemente ya no existe): {e}")

    print("📁 Creando colección vacía...")
    client.get_or_create_collection("docs")

    print("\n🚀 Ejecutando ingest.py con el mismo intérprete de Python (venv)...\n")

    # 🔥 Esto asegura que use el Python actual (el del .venv)
    subprocess.run([sys.executable, "ingest.py"], check=True)

    print("\n🎉 Re-ingesta completada.")

if __name__ == "__main__":
    main()
