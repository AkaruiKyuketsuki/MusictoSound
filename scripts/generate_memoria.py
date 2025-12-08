import subprocess
import json
from datetime import datetime
import os
import time
import openai

# ==========================================================
#   MANEJO ROBUSTO DE EXCEPCIONES DEL SDK OPENAI
# ==========================================================

try:
    from openai import OpenAIError
    from openai.error import RateLimitError
except Exception:
    # Si la estructura del paquete OpenAI cambia (como en SDK v1.0+), 
    # definimos clases de fallback para evitar romper el script.
    class RateLimitError(Exception):
        pass

    class OpenAIError(Exception):
        pass


# ==========================================================
#   CONFIGURACIÓN GENERAL
# ==========================================================

DATA_FILE = "docs/memoria_data.json"
OUTPUT_FILE = "docs/capitulos/04_desarrollo.tex"

# API KEY desde variable de entorno
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Modelo configurable
MODEL = os.environ.get("MODEL", "gpt-4.1-mini")


# ==========================================================
#   FUNCIONES DE UTILIDAD
# ==========================================================

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
    """Obtiene commits del repositorio en formato hash;fecha;mensaje."""
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

def group_commits_by_date(commits):
    """Agrupa commits por fecha: { 'YYYY-MM-DD': [commits...] }."""
    grouped = {}
    for c in commits:
        grouped.setdefault(c["date"], []).append(c)
    return grouped


# ==========================================================
#   FALLBACK SIN OPENAI (funciona incluso sin crédito)
# ==========================================================
"""
def generate_plain_text(commits):
    Versión simple sin llamar a la API (fallback).
    text = "\n\n% === AUTO-GENERATED ENTRY (FALLBACK) ===\n"
    for c in commits:
        text += f"\\section*{{Avances del {c['date']}}}\n"
        text += f"{c['message'].capitalize()}.\n\n"
    text += "% Nota: Este texto se generó sin usar la API (fallback: cuota agotada o error).\n"
    return text
"""
def generate_plain_text(commits):
    """
    Versión simple sin llamar a la API (fallback).

    - Una sola sección por día: \section{Avances del YYYY-MM-DD}
    - Dentro, un bloque por commit con \subsection*{<título basado en el mensaje>}
    """
    grouped = group_commits_by_date(commits)

    text = "\n\n% === AUTO-GENERATED ENTRY (FALLBACK) ===\n"
    for date_str in sorted(grouped.keys()):
        # Sección por día (sale en el índice)
        text += f"\\section{{Avances del {date_str}}}\n\n"
        for c in grouped[date_str]:
            # Título bonito a partir del mensaje del commit
            raw_msg = c["message"].strip()
            title = raw_msg[0].upper() + raw_msg[1:] if raw_msg else "Cambio en el código"

            text += f"\\subsection*{{{title}}}\n"
            text += (
                "En esta fecha se realizó el siguiente cambio en el repositorio: "
                f"{title}.\n\n"
            )

    text += "% Nota: Este texto se generó sin usar la API (fallback: cuota agotada o error).\n"
    return text



# ==========================================================
#   GENERACIÓN ACADÉMICA CON OPENAI (si hay crédito)
# ==========================================================

def generate_academic_text(commits):
    """Genera texto académico en LaTeX usando OpenAI."""
     # Agrupamos por fecha para que el modelo siga esa estructura
    grouped = group_commits_by_date(commits)

    commits_json = json.dumps(commits, indent=2, ensure_ascii=False)
    
    prompt = f"""
Eres un asistente experto en redacción académica y ayudarás a escribir
el capítulo de Desarrollo de un TFG de Ingeniería Informática.

Genera un texto académico en LaTeX basado en los avances siguientes, Te paso los commits NUEVOS agrupados por fecha en este JSON:

{commits_json}

La estructura del JSON es:
{{
  "YYYY-MM-DD": [
    {{ "hash": "abc123...", "message": "mensaje del commit" }},
    ...
  ],
  ...
}}

Requisitos de formato (muy importante):
- Organiza la explicación por FECHAS.
- Para cada fecha genera UNA ÚNICA sección:
    \\section{{Avances del YYYY-MM-DD}}
  (sin asterisco, para que salga en el índice).
- Dentro de cada fecha, para cada commit de ese día:
    - Crea un subtítulo SIN número:
        \\subsection*{{TÍTULO DEL CAMBIO>}}
      donde <TÍTULO DEL CAMBIO> es una frase corta y descriptiva
      basada en el mensaje del commit (NO incluyas la palabra "Commit"
      ni el hash literal).
    -Debajo de ese subtítulo escribe uno o varios párrafos de texto académico
      explicando ese cambio: contexto, propósito, impacto técnico,
      decisiones de diseño, posibles problemas resueltos, etc.

- Estilo:
    - Redacción formal, clara y técnica, en español.
    - No repitas literalmente los mensajes de commit: interprétalos y
      conviértelos en un relato coherente del desarrollo.
    - Puedes agrupar varios commits relacionados en un mismo párrafo si tiene sentido,
      pero mantén un subtítulo por commit para que la estructura quede clara.

- Formato LaTeX:
    - NO añadas preámbulo (ni \\documentclass, ni \\begin{{document}}, etc.).
    - Devuelve ÚNICAMENTE \\section{{...}}, \\subsection*{{...}} y los párrafos de texto.
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

            # ACCESO CORRECTO PARA SDK NUEVO
            return response.choices[0].message.content

        except RateLimitError:
            tries += 1
            if tries > max_retries:
                raise
            print(f"[RateLimit] Reintentando en {backoff}s ({tries}/{max_retries})...")
            time.sleep(backoff)
            backoff *= 2

        except OpenAIError as e:
            tries += 1
            if tries > max_retries:
                raise
            print(f"[OpenAIError] {e}. Reintentando en {backoff}s...")
            time.sleep(backoff)
            backoff *= 2


# ==========================================================
#   GUARDAR EN LA MEMORIA LaTeX
# ==========================================================

def append_to_latex(text):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(text)
        f.write("\n")


# ==========================================================
#   MAIN
# ==========================================================

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

    # Llamada a OpenAI con fallback
    try:
        text = generate_academic_text(new_commits)
    except RateLimitError:
        print("[Fallback] Límite de cuota alcanzado. Usando generación simple.")
        text = generate_plain_text(new_commits)
    except Exception as e:
        print(f"[Fallback] Error inesperado al llamar a OpenAI: {e}")
        text = generate_plain_text(new_commits)

    append_to_latex(text)
    save_commits(current)

    print("Memoria actualizada correctamente.")


if __name__ == "__main__":
    main()
