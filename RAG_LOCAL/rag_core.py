# rag_core.py
import re
import requests
from datetime import datetime

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from config import (
    CHROMA_DIR,
    EMBEDDING_MODEL_NAME,
    OLLAMA_URL,
    TOP_K,
)
from model_router import elegir_modelo

_chroma_client = None
_collection = None
_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        print(f"🧠 Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}")
        _embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedder


def get_collection():
    global _chroma_client, _collection
    if _chroma_client is None:
        print(f"📚 Iniciando Chroma PersistentClient en: {CHROMA_DIR}")
        _chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    if _collection is None:
        _collection = _chroma_client.get_or_create_collection(name="docs")
    return _collection


def parsear_filtros_y_pregunta(texto: str) -> tuple[dict, str]:
    """
    Filtros posibles:
      [type:pdf] [type:docx] ...
      [carpeta:seguridad]
      [fecha>=YYYY-MM-DD]
      [fecha<=YYYY-MM-DD]
    """
    filtros = {
        "exts": set(),
        "carpetas": set(),
        "fecha_desde": None,
        "fecha_hasta": None,
    }

    patron = r'^\s*(\[(?:[^\[\]]+)\]\s*)+'
    match = re.match(patron, texto)
    header = ""
    if match:
        header = match.group(0)

    if header:
        tags = re.findall(r'\[([^\[\]]+)\]', header)
        for tag in tags:
            t = tag.strip()
            if t.lower().startswith("type:"):
                ext = t.split(":", 1)[1].strip().lower()
                if not ext.startswith("."):
                    ext = "." + ext
                filtros["exts"].add(ext)
            elif t.lower().startswith("carpeta:"):
                carpeta = t.split(":", 1)[1].strip().lower()
                if carpeta:
                    filtros["carpetas"].add(carpeta)
            elif t.lower().startswith("fecha>="):
                valor = t.split(">=", 1)[1].strip()
                try:
                    filtros["fecha_desde"] = datetime.strptime(valor, "%Y-%m-%d").date()
                except ValueError:
                    pass
            elif t.lower().startswith("fecha<="):
                valor = t.split("<=", 1)[1].strip()
                try:
                    filtros["fecha_hasta"] = datetime.strptime(valor, "%Y-%m-%d").date()
                except ValueError:
                    pass

    pregunta_limpia = texto[len(header):].strip() if header else texto.strip()
    return filtros, pregunta_limpia


def buscar_contexto(pregunta: str, filtros: dict, k: int = TOP_K) -> list[dict]:
    collection = get_collection()
    embedder = get_embedder()

    pregunta_embedding = embedder.encode([pregunta]).tolist()[0]

    results = collection.query(
        query_embeddings=[pregunta_embedding],
        n_results=max(k * 4, k),
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    context_chunks = []
    for doc, meta in zip(docs, metas):
        context_chunks.append({
            "text": doc,
            "metadata": meta,
        })

    if not context_chunks:
        return []

    filtrados = []

    for ch in context_chunks:
        meta = ch["metadata"]
        ext = meta.get("ext", "").lower()
        folder = meta.get("folder", "").lower()
        date_str = meta.get("date")

        if filtros["exts"] and ext not in filtros["exts"]:
            continue

        if filtros["carpetas"]:
            folder_ok = any(c in folder for c in filtros["carpetas"])
            source = meta.get("source", "").lower()
            if not folder_ok and not any(c in source for c in filtros["carpetas"]):
                continue

        if (filtros["fecha_desde"] or filtros["fecha_hasta"]) and date_str:
            try:
                d = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                d = None
            if d:
                if filtros["fecha_desde"] and d < filtros["fecha_desde"]:
                    continue
                if filtros["fecha_hasta"] and d > filtros["fecha_hasta"]:
                    continue

        filtrados.append(ch)

    if not filtrados:
        return []

    return filtrados[:k]


def construir_prompt(context_chunks: list[dict], pregunta: str) -> str:
    partes = []
    if context_chunks:
        partes.append(
            "A continuación tienes fragmentos de contexto de mis documentos.\n"
            "Cada fragmento indica de qué archivo proviene:\n"
        )
        for i, ch in enumerate(context_chunks, start=1):
            meta = ch["metadata"]
            src = meta.get("source", "desconocido")
            idx = meta.get("chunk_index", "?")
            partes.append(
                f"[FRAGMENTO {i} | {src} | chunk {idx}]\n{ch['text']}\n"
            )
        partes.append(
            "\nUsa estos fragmentos SOLO si son relevantes. "
            "Si no son suficientes, dilo claramente.\n"
        )
    else:
        partes.append(
            "No se encontró contexto relevante en la base de documentos para esta pregunta.\n"
            "Responde solo con tu conocimiento general y aclara que no hay contexto.\n"
        )

    partes.append("\n[PREGUNTA DEL USUARIO]\n")
    partes.append(pregunta)

    return "\n".join(partes)


def llamar_ollama(modelo: str, prompt: str) -> str:
    # Payload para /api/chat sin streaming
    payload = {
        "model": modelo,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Eres un asistente técnico. "
                    "Si usas información de los fragmentos, cítala de forma clara. "
                    "Si no hay información suficiente en el contexto, dilo."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "stream": False,  # 👈 clave para que devuelva UN solo JSON
    }

    # Tu OLLAMA_URL ya viene como "http://localhost:11434/api/chat"
    url = OLLAMA_URL

    resp = requests.post(url, json=payload, timeout=600)
    resp.raise_for_status()

    # Intentamos parsear JSON, si falla mostramos el texto para debug
    try:
        data = resp.json()
    except Exception:
        print("\n⚠ Respuesta NO-JSON desde Ollama (debug):\n")
        print(resp.text[:1000])
        raise

    # Estructura típica de /api/chat:
    # {
    #   "message": {
    #       "role": "assistant",
    #       "content": "texto..."
    #   },
    #   ...
    # }
    message = data.get("message", {})
    content = message.get("content", "")

    return content.strip()



def responder(texto_usuario: str) -> tuple[str, str, list[str]]:
    filtros, pregunta = parsear_filtros_y_pregunta(texto_usuario)

    modelo = elegir_modelo(pregunta)
    print(f"🤖 Modelo elegido: {modelo}")

    context_chunks = buscar_contexto(pregunta, filtros=filtros, k=TOP_K)

    fuentes = []
    for ch in context_chunks:
        src = ch["metadata"].get("source")
        if src and src not in fuentes:
            fuentes.append(src)

    prompt = construir_prompt(context_chunks, pregunta)
    respuesta = llamar_ollama(modelo, prompt)

    return modelo, respuesta, fuentes
