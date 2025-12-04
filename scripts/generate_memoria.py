import subprocess
import json
from datetime import datetime
import os

# Archivos del sistema
DATA_FILE = "docs/memoria_data.json"
OUTPUT_FILE = "docs/capitulos/04_desarrollo.tex"

def load_saved_commits():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_commits(commits):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(commits, f, indent=4)

def get_git_commits():
    """Obtiene commits en formato: hash;fecha;mensaje"""
    result = subprocess.run(
        ["git", "log", "--pretty=format:%H;%ad;%s", "--date=short"],
        stdout=subprocess.PIPE,
        text=True
    )

    commits = []
    for line in result.stdout.split("\n"):
        parts = line.split(";")
        if len(parts) == 3:
            commits.append({
                "hash": parts[0],
                "date": parts[1],
                "message": parts[2]
            })

    return commits

def generate_plain_text(commits):
    """Texto básico (sin ChatGPT aún)."""
    text = "\n\n% === AUTO-GENERATED ENTRY ===\n"

    for c in commits:
        text += f"\\section*{{Commit del {c['date']}}}\n"
        text += f"{c['message'].capitalize()}.\n\n"

    return text

def append_to_latex(text):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(text)

def main():
    print("Procesando commits...")

    saved = load_saved_commits()
    current = get_git_commits()

    saved_hashes = {c["hash"] for c in saved}

    # Detectar commits nuevos
    new_commits = [c for c in current if c["hash"] not in saved_hashes]

    if not new_commits:
        print("No hay commits nuevos.")
        return

    print(f"Encontrados {len(new_commits)} commits nuevos.")

    # Generar texto para LaTeX
    text = generate_plain_text(new_commits)

    # Añadir a la memoria
    append_to_latex(text)

    # Guardar commits procesados
    save_commits(current)

    print("Memoria actualizada correctamente.")

if __name__ == "__main__":
    main()
