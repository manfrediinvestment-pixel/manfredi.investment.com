#!/usr/bin/env python3
"""
Daily report updater — uses Claude with web search to fetch real-time data
and writes structured JSON files for Argentina and Wall Street reports.
Run daily at 11:00 AM via cron.
"""

import anthropic
import json
import os
import re
import time
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def generar_reporte(prompt_file: str, output_file: str):
    prompt = (SCRIPT_DIR / prompt_file).read_text(encoding="utf-8")
    messages = [{"role": "user", "content": prompt}]

    # Multi-turn loop: web_search tool may require several turns before
    # Claude emits the final text response.
    for turn in range(6):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search"}],
            messages=messages,
        )

        print(f"  turn {turn+1}: stop_reason={response.stop_reason}, "
              f"blocks={[b.type for b in response.content]}")

        # Concatenate ALL text blocks (response comes fragmented)
        text_parts = [b.text for b in response.content if b.type == "text" and b.text.strip()]
        texto_completo = "\n".join(text_parts).strip()

        if response.stop_reason == "end_turn" and texto_completo:
            texto = texto_completo
            break

        if response.stop_reason == "tool_use":
            # Shouldn't happen with server-side web_search, but handle defensively
            messages.append({"role": "assistant", "content": response.content})
            tool_results = [
                {"type": "tool_result", "tool_use_id": b.id, "content": "Done."}
                for b in response.content if b.type == "tool_use"
            ]
            messages.append({"role": "user", "content": tool_results})
            continue

        if texto_completo:
            texto = texto_completo
            break
    else:
        raise ValueError(f"No se obtuvo texto tras 6 turnos para {prompt_file}")

    if not texto:
        raise ValueError(f"Texto vacío en respuesta para {prompt_file}")

    # Extraer bloque JSON del texto (ignorar texto antes/después)
    json_match = re.search(r"\{[\s\S]*\}", texto)
    if not json_match:
        raise ValueError(f"No se encontró bloque JSON en la respuesta para {prompt_file}")
    json_str = json_match.group(0)

    # Validar que sea JSON válido
    data = json.loads(json_str)

    # Agregar timestamp de actualización
    data["updated_at"] = datetime.now().strftime("%H:%M")
    data["status"] = "ok"

    output_path = SCRIPT_DIR / output_file
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  ✓ {output_file} guardado ({len(data.get('noticias', []))} noticias)")


def main():
    print(f"[{datetime.now().isoformat()}] Iniciando actualización de reportes...")

    try:
        print("→ Generando reporte Argentina...")
        generar_reporte("agent-prompt-argentina.md", "reports/argentina.json")
    except Exception as e:
        print(f"  ✗ Error Argentina: {e}")

    # Pausa para evitar rate limit entre los dos requests pesados
    print("  Esperando 120s antes del siguiente reporte...")
    time.sleep(120)

    try:
        print("→ Generando reporte Wall Street...")
        generar_reporte("agent-prompt-wallstreet.md", "reports/wallstreet.json")
    except Exception as e:
        print(f"  ✗ Error Wall Street: {e}")

    print("Finalizado.")


if __name__ == "__main__":
    main()
