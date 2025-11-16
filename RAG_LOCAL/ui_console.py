# ui_console.py
from rag_core import responder

def main():
    print("=======================================")
    print("   RAG LOCAL - CONSOLA (D:\\RAG_LOCAL)")
    print("=======================================\n")
    print("Comandos especiales:")
    print("  /phi   → Forzar modelo phi4 (profundo)")
    print("  /code  → Forzar modelo mistral (código)")
    print("  /llama → Forzar modelo llama3.1 (equilibrado)")
    print("\nFiltros opcionales (puedes combinar al inicio):")
    print("  [type:pdf]           → solo PDFs")
    print("  [type:docx]          → solo Word")
    print("  [type:xlsx]          → solo Excel")
    print("  [type:pptx]          → solo PowerPoint")
    print("  [carpeta:seguridad]  → solo archivos en carpetas que contengan 'seguridad'")
    print("  [fecha>=2024-01-01]  → solo archivos modificados desde esa fecha")
    print("  [fecha<=2023-12-31]  → solo archivos hasta esa fecha")
    print("\nEjemplos:")
    print("  [type:pdf] dame un resumen de mis políticas")
    print("  [carpeta:seguridad] /phi analiza mis notas de hardening")
    print("  [fecha>=2024-01-01] dime lo más reciente sobre negociación\n")
    print("Escribe 'salir' para terminar.\n")

    while True:
        try:
            pregunta = input("🧩 Pregunta> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Saliendo...")
            break

        if not pregunta:
            continue

        if pregunta.lower() in ["salir", "exit", "quit"]:
            print("👋 Saliendo...")
            break

        modelo, respuesta, fuentes = responder(pregunta)
        print(f"\n[Modelo usado: {modelo}]\n")
        print(respuesta)

        if fuentes:
            print("\n📂 Fuentes usadas:")
            for src in fuentes:
                print(f" - {src}")
        else:
            print("\n📂 Fuentes usadas: (sin contexto de documentos, solo conocimiento del modelo)")

        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    main()
