# rag_query.py - RAG sobre Chroma usando phi4 como modelo principal

import textwrap

import chromadb
import requests
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    EMBEDDING_MODEL_NAME,
    TOP_K,
    OLLAMA_URL,
    MODEL_MAIN,  # aquí tienes "phi4:14b-q4_K_M"
)


# 🔁 Opcional: cache simple para no recargar el modelo cada vez
_embedder = None
_collection = None


def get_embedder():
    global _embedder
    if _embedder is None:
        print(f"🧠 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}...")
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def get_collection():
    global _collection
    if _collection is None:
        print(f"📚 Conectando a Chroma en: {CHROMA_DIR}")
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = client.get_or_create_collection("docs")
    return _collection


def _build_context(docs, metadatas):
    """
    Construye un bloque de contexto legible a partir de los documentos y metadatos.
    docs y metadatas vienen como listas de listas desde Chroma:
      docs[0] -> lista de documentos
      metadatas[0] -> lista de metadatas correspondientes
    """
    if not docs or not docs[0]:
        return ""

    context_parts = []
    for idx, (doc, meta) in enumerate(zip(docs[0], metadatas[0])):
        source = meta.get("source", "desconocido")
        chunk_index = meta.get("chunk_index", "N/A")
        context_parts.append(
            f"[Fragmento {idx+1} | chunk {chunk_index} | fuente: {source}]\n{doc}"
        )

    return "\n\n".join(context_parts)


def _call_ollama_rag(model: str, context: str, question: str) -> str:
    """
    Llama al modelo vía Ollama usando el contexto recuperado de Chroma.
    Usa MODEL_MAIN (phi4) por defecto.
    """
    system_prompt = (
        "Eres un asistente especializado que responde basándote en el CONTEXTO "
        "proporcionado. Si la respuesta no está claramente respaldada por el contexto, "
        "indícalo y responde de forma honesta. Responde siempre en español, de forma "
        "clara y directa."
    )

    user_prompt = textwrap.dedent(
        f"""
        CONTEXTO:

        {context}

        ----------

        PREGUNTA:

        {question}

        ----------

        Instrucciones:
        - Usa únicamente la información del CONTEXTO para responder.
        - Si algo no está en el contexto, dilo explícitamente.
        - Puedes citar partes importantes del contexto si ayuda a la explicación.
        """
    ).strip()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    msg = data.get("message", {})
    text = msg.get("content", "") or ""
    return text.strip()


def rag_query(question: str) -> str:
    """
    Hace una consulta RAG:
    - Embebe la pregunta
    - Recupera TOP_K fragmentos relevantes de Chroma
    - Llama a phi4 (MODEL_MAIN) con el contexto
    - Devuelve la respuesta en texto
    """
    question = question.strip()
    if not question:
        raise ValueError("La pregunta no puede estar vacía.")

    embedder = get_embedder()
    collection = get_collection()

    print(f"\n🔎 Pregunta al RAG: {question}\n")

    # 1) Embedding de la pregunta
    query_embedding = embedder.encode([question]).tolist()

    # 2) Consulta a Chroma
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=TOP_K,
        include=["documents", "metadatas", "distances"],
    )

    docs = results.get("documents", [[]])
    metadatas = results.get("metadatas", [[]])
    distances = results.get("distances", [[]])

    if not docs or not docs[0]:
        print("⚠ No se encontraron fragmentos relevantes en la base vectorial.")
        return "No encontré información relevante en tus documentos para responder esta pregunta."

    print(f"📄 Fragmentos recuperados: {len(docs[0])}")
    # Opcional: mostrar distancias si quieres depurar
    # print("Distancias:", distances[0])

    # 3) Construir contexto
    context = _build_context(docs, metadatas)

    # 4) Llamar al modelo principal (phi4) vía Ollama
    print(f"🤖 Consultando modelo RAG: {MODEL_MAIN} (Ollama)...\n")
    answer = _call_ollama_rag(MODEL_MAIN, context, question)

    return answer


def ask_rag(question: str):
    """
    Envoltorio cómodo para usar desde otros scripts (ej: smart_query, pruebas en consola).
    Imprime la respuesta formateada y la devuelve.
    """
    try:
        answer = rag_query(question)
    except Exception as e:
        print(f"❌ Error en RAG: {e}")
        return None

    print("\n🧠 RESPUESTA DEL RAG:")
    print("───────────────────────")
    print(answer)
    print("───────────────────────")
    return answer


if __name__ == "__main__":
    # Permite probar este archivo directamente con:
    # (.venv) python rag_query.py
    import sys as _sys

    if len(_sys.argv) > 1:
        q = " ".join(_sys.argv[1:])
    else:
        q = input("Escribe tu pregunta para el RAG: ").strip()

    ask_rag(q)
