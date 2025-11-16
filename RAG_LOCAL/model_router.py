# model_router.py
from config import MODEL_MAIN, MODEL_CODE, MODEL_BALANCED

def elegir_modelo(pregunta: str) -> str:
    """
    Decide qué modelo usar según el contenido de la pregunta.
    También permite forzar modelo con prefijos:
      /phi   → phi4
      /code  → mistral
      /llama → llama3.1:8b
    """
    q = pregunta.strip()
    q_lower = q.lower()

    # 1) Prefijos manuales
    if q_lower.startswith("/phi "):
        return MODEL_MAIN
    if q_lower.startswith("/code "):
        return MODEL_CODE
    if q_lower.startswith("/llama "):
        return MODEL_BALANCED

    # 2) Reglas automáticas básicas

    # Preguntas de código / programación
    palabras_codigo = [
        "codigo", "código", "code", "java", "python", "script",
        "funcion", "función", "método", "error de compilación",
        "stack trace", "excepcion", "excepción"
    ]
    if any(p in q_lower for p in palabras_codigo):
        return MODEL_CODE

    # Preguntas cortas → modelo equilibrado para ir rápido
    if len(q_lower.split()) < 10:
        return MODEL_BALANCED

    # Preguntas largas de análisis → phi4
    palabras_analisis = [
        "analiza", "analizar", "riesgos", "resumen", "conclusiones",
        "detallado", "explicame", "explícame", "profundo", "hardening",
        "plan", "arquitectura", "diseño"
    ]
    if any(p in q_lower for p in palabras_analisis):
        return MODEL_MAIN

    # Por defecto, modelo equilibrado
    return MODEL_BALANCED
