# 🧠 RAG Local – IA privada con Ollama + ChromaDB

Sistema **RAG (Retrieval-Augmented Generation)** completamente local que combina **Ollama**, **ChromaDB** y **embeddings** para consultar tus propios documentos (PDF, Word, Excel, PowerPoint, TXT y Markdown) sin subir nada a la nube.

Está pensado para estudio, ciberseguridad, informática forense y laboratorio personal.

---

## 📌 Descripción corta

Sistema RAG local que usa Ollama y ChromaDB para buscar y responder preguntas basadas en tus documentos. Incluye un menú interactivo, una consola avanzada (`ui_console.py`) y un router inteligente que decide si tu pregunta es de chat general, código o debe usar el RAG con tus archivos. Todo corre **100% offline**.

---

## 📚 Documentación (HTML)

Este repositorio incluye ** guía en HTML** dentro del proyecto:

- `guia_rag_local.html` → **Guía completa**  
  Explica conceptos (RAG, embeddings), estructura del proyecto, instalación detallada, uso del menú, flujo de trabajo, etc.



Toda la explicación paso a paso (incluyendo rutas C:\ o D:\, entorno virtual, librerías, accesos directos y ejemplos) está documentada allí, para no saturar este README.

---

## 🔧 Requisitos principales

- ✅ **Python 3.11.9 (recomendado y probado)**  
  Se recomienda específicamente **Python 3.11.9** para evitar problemas de compatibilidad con:
  - ChromaDB  
  - Modelos de embeddings  
  - Dependencias internas de las librerías usadas  

- ✅ **Ollama instalado** (para ejecutar modelos locales):
  - `phi4:14b-q4_K_M` – modelo principal para RAG  
  - `llama3.1:8b` – modelo equilibrado para chat general  
  - `mistral` – orientado a código/programación  

- ✅ **Windows 10/11**  
  Proyecto pensado para entorno Windows con PowerShell.

---

## ⚙️ ¿Qué hace este proyecto?

- Lee tus documentos en la carpeta `docs/` (PDF, DOCX, PPTX, XLSX, TXT, MD).
- Los transforma en chunks de texto y genera **embeddings**.
- Guarda todo en **ChromaDB** como base vectorial.
- Cuando haces una pregunta, el sistema:
  1. Analiza tu consulta.
  2. Decide si es:
     - Chat general,
     - Pregunta de código
     - o una consulta que debe usar tus documentos (RAG).
  3. Busca los fragmentos más relevantes en tus archivos.
  4. Construye un contexto y se lo envía al modelo de Ollama.
  5. Te responde en español, citando tus documentos cuando corresponde.

---

## 🗂 Estructura general (resumen)

En la carpeta principal del proyecto (`RAG_LOCAL/`) encontrarás, entre otros:

- `docs/` → aquí van tus documentos.  
- `chroma_db/` → base de datos vectorial (se genera automáticamente).  
- `bat/` → scripts `.bat` para iniciar el menú fácilmente.  
- `.venv/` → entorno virtual de Python.  

Scripts clave:

- `config.py` → rutas, modelos y parámetros del RAG.  
- `ingest.py` / `re_ingest.py` → ingestan tus documentos en ChromaDB.  
- `rag_core.py` → núcleo del RAG (búsqueda + llamada a Ollama).  
- `smart_query.py` → router inteligente (chat / código / documentos).  
- `rag_menu.py` → menú principal del sistema.  
- `ui_console.py` → consola avanzada que habla directamente con el RAG.  
- `guia_rag_local.html` → guía completa del proyecto.  
- `guia_rag_local_resumen.html` → resumen / checklist.  

---

## 🖥 Formas de uso (resumen)

En la guía HTML se detalla todo, pero a alto nivel:

1. Colocas tus documentos en `docs/`.
2. Ejecutas el menú (`rag_menu.py`) mediante:
   - un `.bat` en la carpeta `bat/`, o
   - directamente desde PowerShell con el entorno virtual activado.
3. Desde el menú puedes:
   - Re-ingestar documentos,
   - Limpiar la colección,
   - Contar chunks,
   - Entrar a modo chat,
   - Hacer preguntas rápidas,
   - Abrir `ui_console.py` (consola avanzada conectada al RAG).

---

## 🔒 Privacidad

- Todo corre en tu PC.
- No se envían documentos ni consultas a servidores externos.
- Ideal para:
  - Apuntes de estudio,
  - Material de ciberseguridad / forense,
  - Documentos internos y sensibles.

---

## 👨‍💻 Autor

Proyecto diseñado y documentado para uso personal, estudio y laboratorio de ciberseguridad, con foco en:

- IA local  
- RAG práctico  
- Seguridad y privacidad de la información

Si este proyecto te resulta útil, una ⭐ en el repositorio siempre es bienvenida.
