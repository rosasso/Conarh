#!/usr/bin/env python3
"""Monta os HTML únicos (offline) da apresentação 'O Universo Kavuka'.

Gera duas versões a partir de dois templates:
  index.html    <- src/template.html            (6 telas — a que vai pro estande)
  completo.html <- src/template-completo.html   (17 telas — versão longa, reunião)

Em cada uma substitui os placeholders pelos data-URIs dos assets:
  - logo e mascote da marca (extraídos da apresentação do CONARH)
  - prints reais dos 3 ambientes (src/shots/*.jpg)

Uso:  python3 src/build.py
"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
SHOTS = SRC / "shots"

SHOT_MAP = {
    "__SHOT_KANBAN__": "c_kanban.jpg",   # gestor · kanban geral
    "__SHOT_ANA__": "c_ana.jpg",         # gestor · dossiê do candidato
    "__SHOT_VHOME__": "v_home.jpg",      # kavukavagas · home (produção)
    "__SHOT_VVAGAS__": "v_vagas.jpg",    # kavukavagas · lista de vagas (produção)
    "__SHOT_VHOME2__": "v_home2.jpg",    # kavukavagas · home nova (produção, ago/2026)
    "__SHOT_VPORTAS__": "v_portas.jpg",  # kavukavagas · as duas portas de entrada (/entrar)
    "__SHOT_PME__": "p_me.jpg",          # portal do candidato
    "__SHOT_KYID__": "p_kyid.jpg",       # KYID pública
    "__SHOT_RADAR__": "c_radar.jpg",     # radar 13 dimensões (Caique)
    "__SHOT_CAIQUE__": "c_caique.jpg",   # dossiê do candidato (Caique)
}

BUILDS = [
    ("template.html", "index.html", "6 telas"),
    ("template-completo.html", "completo.html", "17 telas"),
]


def data_uri(path: pathlib.Path) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()


logo = (SRC / "logo.b64.txt").read_text().strip()
mascot = (SRC / "mascot_s.b64.txt").read_text().strip()
shots = {}
for token, fname in SHOT_MAP.items():
    f = SHOTS / fname
    if not f.exists():
        raise SystemExit(f"print faltando: {f}")
    shots[token] = data_uri(f)

for tpl_name, out_name, label in BUILDS:
    tpl = SRC / tpl_name
    if not tpl.exists():
        print(f"  (pulando {out_name}: {tpl_name} não existe)")
        continue
    html = tpl.read_text(encoding="utf-8")
    html = html.replace("__LOGO__", logo).replace("__MASCOT__", mascot)
    for token, uri in shots.items():
        html = html.replace(token, uri)

    leftover = [t for t in ["__LOGO__", "__MASCOT__", *SHOT_MAP] if t in html]
    if leftover:
        raise SystemExit(f"{out_name}: placeholder não substituído: {leftover}")

    out = ROOT / out_name
    out.write_text(html, encoding="utf-8")
    print(f"{out_name:15s} ({label})  {out.stat().st_size/1024/1024:.2f} MB")

print("ok — sem placeholders pendentes")
