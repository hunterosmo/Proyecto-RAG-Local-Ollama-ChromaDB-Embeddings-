# rag_menu.py - Menú principal del RAG local

import os
import sys
import time

# Importamos las funciones que ya tienes
try:
    from re_ingest import main as re_ingest_main
except ImportError:
    re_ingest_main = None

try:
    from clean_collection import main as clean_collection_main
except ImportError:
    clean_collection_main = None

try:
    from count_collection import main as count_collection_main
except ImportError:
    count_collection_main = None

try:
    from smart_query import smart_ask
except ImportError:
    smart_ask = None


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause(msg: str = "\nPresiona ENTER para volver al menú..."):
    input(msg)


def option_re_ingest():
    clear_screen()
    print("🔄 RE-INGESTAR DOCUMENTOS\n")
    if re_ingest_main is None:
        print("⚠ No se encontró re_ingest.py o su función main().")
    else:
        re_ingest_main()
    pause()


def option_clean_collection():
    clear_screen()
    print("🧹 LIMPIAR COLECCIÓN 'docs'\n")
    if clean_collection_main is None:
        print("⚠ No se encontró clean_collection.py o su función main().")
    else:
        clean_collection_main()
    pause()


def option_count_collection():
    clear_screen()
    print("📊 CONTAR DOCUMENTOS/CHUNKS EN 'docs'\n")
    if count_collection_main is None:
        print("⚠ No se encontró count_collection.py o su función main().")
    else:
        count_collection_main()
    pause()


def option_chat_mode():
    clear_screen()
    print("💬 MODO CHAT CON EL RAG")
    print("Escribe tus preguntas. Escribe 'salir' para volver al menú.\n")

    if smart_ask is None:
        print("⚠ No se encontró smart_query.py o la función smart_ask.")
        pause()
        return

    while True:
        q = input("🧠 Pregunta: ").strip()
        if q.lower() in ("salir", "exit", "q"):
            break
        if not q:
            continue
        try:
            smart_ask(q)
        except Exception as e:
            print(f"❌ Error durante la consulta: {e}")
    pause("\nSaliendo del modo chat. Presiona ENTER para volver al menú...")


def option_single_question():
    clear_screen()
    print("❓ PREGUNTA ÚNICA AL RAG\n")

    if smart_ask is None:
        print("⚠ No se encontró smart_query.py o la función smart_ask.")
        pause()
        return

    q = input("Escribe tu pregunta: ").strip()
    if not q:
        print("⚠ No ingresaste ninguna pregunta.")
        pause()
        return

    try:
        smart_ask(q)
    except Exception as e:
        print(f"❌ Error durante la consulta: {e}")

    pause()


# 🔥 ESTA ES LA ÚNICA FUNCIÓN QUE AGREGAMOS
def option_ui_console():
    clear_screen()
    print("🖥 Abriendo UI de consola avanzada (ui_console.py)...\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = sys.executable or "python"

    # Nos aseguramos de estar en la carpeta del proyecto
    os.chdir(script_dir)

    # Ejecutamos ui_console.py
    cmd = f'"{python_exe}" ui_console.py'
    os.system(cmd)

    pause("\nui_console.py ha terminado. Presiona ENTER para volver al menú...")


def main_menu():
    os.system("title RAG LOCAL - MENU") if os.name == "nt" else None

    while True:
        clear_screen()
        print("══════════════════════════════════════════")
        print("          MENÚ RAG LOCAL - CHROMA         ")
        print("══════════════════════════════════════════")
        print(" 1) Re-ingestar documentos (limpia + indexa)")
        print(" 2) Limpiar colección 'docs'")
        print(" 3) Contar documentos/chunks")
        print(" 4) Modo chat (múltiples preguntas)")
        print(" 5) Pregunta única rápida con el RAG")
        print(" 6) Salir")
        print(" 7) Abrir ui_console.py (consola avanzada)")   # ← AGREGADO
        print("══════════════════════════════════════════")

        choice = input("Selecciona una opción (1-7): ").strip()

        if choice == "1":
            option_re_ingest()
        elif choice == "2":
            option_clean_collection()
        elif choice == "3":
            option_count_collection()
        elif choice == "4":
            option_chat_mode()
        elif choice == "5":
            option_single_question()
        elif choice == "6":
            print("\nSaliendo del menú RAG. ¡Hasta luego! 👋")
            time.sleep(1)
            break
        elif choice == "7":
            option_ui_console()   # ← AGREGADO
        else:
            print("\n⚠ Opción inválida. Intenta de nuevo.")
            time.sleep(1.2)


if __name__ == "__main__":
    main_menu()
