# smart_query.py - Decide si usar RAG (documentos) o solo el modelo de IA

import requests

from config import (
    OLLAMA_URL,
    MODEL_MAIN,      # para RAG (phi4)
    MODEL_CODE,      # para código (mistral)
    MODEL_BALANCED,  # para chat general (llama3.1:8b)
)

# Importamos el RAG basado en documentos
from rag_query import ask_rag as ask_rag_docs


def _call_ollama_chat(model: str, content: str) -> str:
    """Llama a Ollama en modo chat sin RAG (solo modelo)."""
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": content}
        ],
        "stream": False,
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=600)
    resp.raise_for_status()
    data = resp.json()
    msg = data.get("message", {})
    text = msg.get("content", "") or ""
    return text.strip()


def _is_small_talk(q: str) -> bool:
    """Detecta saludos / charla ligera."""
    ql = q.lower().strip()

    greetings = [
        "hola", "hola!", "buenas", "buenas!", "buenas tardes",
        "buenas noches", "buenos dias", "buenos días",
        "que tal", "qué tal", "como estas", "cómo estás",
        "como has estado", "cómo has estado",
        "hi", "hello", "hey"
    ]

    # Frases muy cortas tipo "hola", "hola cómo estás", etc.
    if len(ql.split()) <= 8 and any(g in ql for g in greetings):
        return True

    return False


def _is_code_question(q: str) -> bool:
    """Detecta si la pregunta es claramente de programación/código."""
    ql = q.lower()

    keywords = [
        # Lenguajes
        "python", "c#", "c++", "java", "javascript", "typescript",
        "powershell", "bash", "shell", "sql",
        # Palabras típicas
        "código", "codigo", "script", "programa", "programación", "programacion",
        "función", "funcion", "clase", "método", "metodo",
        "error", "bug", "traceback", "stack trace", "exception", "excepción",
        # Librerías comunes
        "import ", "def ", "class ", "console.log", "try:", "except",
        "for (", "while ("
    ]

    # Prefijo para forzar código
    if ql.startswith("code:") or ql.startswith("codigo:") or ql.startswith("código:"):
        return True

    # Si hay bloque de código
    if "```" in ql:
        return True

    # Palabras clave
    if any(k in ql for k in keywords):
        return True

    return False


def _is_doc_question(q: str) -> bool:
    """Detecta si la pregunta habla explícitamente de tus documentos/PDFs/apuntes."""
    ql = q.lower()

    # Prefijos para forzar RAG
    if ql.startswith("doc:") or ql.startswith("rag:"):
        return True

    # Frases típicas que indican que quieres usar TUS documentos
    doc_phrases = [
        # Acciones directas
        "revisa en mis documentos",
        "revisar en mis documentos",
        "busca en mis documentos",
        "buscar en mis documentos",
        "usa mis documentos",
        "utiliza mis documentos",
        "usa mis apuntes",
        "utiliza mis apuntes",
        "en mis documentos",
        "en mis apuntes",
        "en mis archivos",
        "en mis pdf",
        "en mis pdfs",

        # Referencias al documento específico
        "según el documento",
        "segun el documento",
        "según el pdf",
        "segun el pdf",
        "según mis apuntes",
        "segun mis apuntes",
        "según el texto",
        "segun el texto",
        "en el documento",
        "en el pdf",
        "en este pdf",
        "en este documento",
        "en ese documento",
        "en ese pdf",
        "en el archivo",
        "en este archivo",
        "en ese archivo",
        "del documento",
        "del pdf",
        "del archivo",

        # Cosas muy típicas de clase
        "según lo que dice el documento",
        "segun lo que dice el documento",
        "según el material",
        "segun el material",
        "según la lectura",
        "segun la lectura",
    ]

    if any(p in ql for p in doc_phrases):
        return True

    # Si menciona página / capítulo y también documento/pdf
    if ("página" in ql or "pagina" in ql or "capítulo" in ql or "capitulo" in ql) and (
        "documento" in ql or "pdf" in ql or "archivo" in ql or "apuntes" in ql
    ):
        return True

    return False


def smart_ask(question: str):
    """
    Decide automáticamente:
    - Small talk / charla general → llama3.1:8b (MODEL_BALANCED)
    - Pregunta de código → mistral (MODEL_CODE)
    - Pregunta sobre documentos → RAG con phi4 + Chroma (MODEL_MAIN)
    - En caso de duda → modelo general (llama3.1:8b)
    """
    q = question.strip()
    if not q:
        print("⚠ Pregunta vacía.")
        return

    q_lower = q.lower()

    # Quitar prefijos si los usas para forzar
    if q_lower.startswith(("doc:", "rag:", "code:", "codigo:", "código:")):
        # separamos "code: ..." o "doc: ..."
        q = q.split(":", 1)[1].strip()
        q_lower = q.lower()

    # 1) Small talk / charla corta
    if _is_small_talk(q):
        print("\n🤖 (Chat general - llama3.1:8b)\n")
        answer = _call_ollama_chat(MODEL_BALANCED, q)
        print(answer)
        return answer

    # 2) Pregunta de código
    if _is_code_question(q):
        print("\n💻 (Pregunta de código - mistral)\n")
        answer = _call_ollama_chat(MODEL_CODE, q)
        print(answer)
        return answer

    # 3) Pregunta explícita sobre documentos
    if _is_doc_question(q):
        print("\n📚 (Usando documentos con RAG - phi4 + Chroma)\n")
        # ask_rag_docs ya imprime la respuesta internamente
        return ask_rag_docs(q)

    # 4) En caso de duda → Chat general
    print("\n🤖 (Chat general - llama3.1:8b)\n")
    answer = _call_ollama_chat(MODEL_BALANCED, q)
    print(answer)
    return answer
