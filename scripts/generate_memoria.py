import subprocess
import json
from datetime import datetime
import os
import time
import openai

# Importar errores específicos de la API
from openai import OpenAIError
from openai.error import RateLimitError

# Archivos del sistema
DATA_FILE = "docs/memoria_data.json"
OUTPUT_FILE = "docs/capitulos/04_desarrollo.tex"

# Leer API KEY desde variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Modelo por defecto (puede ser sobrescrito por variable de entorno)
MODEL = os.environ.get("MODEL", "gpt-4.1-mini")


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
    """Versión simple sin llamar a la API (fallback)."""
    text = "\n\n% === AUTO-GENERATED ENTRY (FALLBACK) ===\n"
    for c in commits:
        text += f"\\section*{{Avances del {c['date']}}}\n"
        text += f"{c['message'].capitalize()}.\n\n"
    text += "% Nota: Este texto se generó sin usar la API (fallback: cuota agotada o error).\n"
    return text


def generate_academic_text(commits):
    """Intenta obtener texto vía OpenAI; si falla por cuota, lanza RateLimitError."""
    commits_json = json.dumps(commits, indent=2, ensure_ascii=False)
    prompt = f"""
Eres un asistente experto en redacción académica y ayudarás a escribir
el capítulo de Desarrollo de un TFG de Ingeniería Informática.

Genera un texto académico en LaTeX explicando los avances siguientes:

{commits_json}

Requisitos:
- Organiza la explicación por fechas.
- Para cada fecha usa un título: \\section*{{Avances del YYYY-MM-DD}}
- Debes escribir un texto fluido, formal y técnico.
- Explica el propósito de cada cambio, su impacto y decisiones de diseño.
- No repitas los mensajes de commit literalmente: interprétalos.
- Escribe solo LaTeX, sin preámbulo.
    """

    tries = 0
    max_retries = 2
    backoff = 2

    while True:
        try:
            response = openai.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "Eres un generador experto de textos académicos en LaTeX."},
                    {"role": "user", "content": prompt}
                ],
                timeout=60
            )
            return response.choices[0].message.content


        except RateLimitError:
            tries += 1
            if tries > max_retries:
                raise
            print(f"RateLimitError: reintentando en {backoff}s ({tries}/{max_retries})")
            time.sleep(backoff)
            backoff *= 2

        except OpenAIError as e:
            tries += 1
            if tries > max_retries:
                raise
            print(f"OpenAIError {e}: reintentando en {backoff}s.")
            time.sleep(backoff)
            backoff *= 2


def append_to_latex(text):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(text)
        f.write("\n")


def main():
    print("Procesando commits...")

    saved = load_saved_commits()
    current = get_git_commits()
    saved_hashes = {c["hash"] for c in saved}
    new_commits = [c for c in current if c["hash"] not in saved_hashes]

    if not new_commits:
        print("No hay commits nuevos.")
        return

    print(f"Encontrados {len(new_commits)} commits nuevos.")

    try:
        text = generate_academic_text(new_commits)
    except RateLimitError:
        print("Quota insuficiente o RateLimit. Generando entrada fallback (sin API).")
        text = generate_plain_text(new_commits)
    except Exception as e:
        print(f"Error inesperado al llamar a la API: {e}")
        print("Generando entrada fallback (sin API).")
        text = generate_plain_text(new_commits)

    append_to_latex(text)
    save_commits(current)

    print("Memoria actualizada correctamente.")


if __name__ == "__main__":
    main()
