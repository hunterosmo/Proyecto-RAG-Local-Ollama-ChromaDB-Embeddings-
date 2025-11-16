# config.py
from pathlib import Path

# Ruta base del proyecto (D:\RAG_LOCAL)
BASE_DIR = Path(__file__).resolve().parent

# Carpeta donde pondrás tus documentos
DOCS_DIR = BASE_DIR / "docs"

# Carpeta donde Chroma guardará la base de datos vectorial
CHROMA_DIR = BASE_DIR / "chroma_db"

# Modelo de embeddings
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# URL de Ollama (por defecto)
OLLAMA_URL = "http://localhost:11434/api/chat"

# Modelos LLM que usarás en Ollama
MODEL_MAIN = "phi4:14b-q4_K_M"   # modelo fuerte (phi4 optimizado)
MODEL_CODE = "mistral"           # programación
MODEL_BALANCED = "llama3.1:8b"   # equilibrado / general

# Parámetros del RAG
TOP_K = 4              # cuántos fragmentos relevantes traer de Chroma
CHUNK_SIZE = 1000      # caracteres por chunk de texto
CHUNK_OVERLAP = 200    # solapamiento entre chunks (en caracteres)