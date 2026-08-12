#!/usr/bin/env python3
"""
Gera o index.html (arquivo único, imagens embutidas) a partir de src/.

  src/app.html   -> layout + estilo + codigo  (e AQUI que se edita)
  src/jobs.json  -> vagas, candidatos e alertas
  src/img/*.png  -> imagens (trocar o arquivo ja troca no app)

Uso:
  python3 build.py          gera index.html (7 MB, arquivo unico, pro tablet)
  python3 build.py --dev    gera src/dev.html (leve, abre rapido pra conferir)
"""
import base64, hashlib, json, mimetypes, pathlib, re, sys

RAIZ = pathlib.Path(__file__).parent
SRC  = RAIZ / "src"

def embutir(caminho_rel: str) -> str:
    """Lê src/<caminho> e devolve uma data URI base64."""
    f = SRC / caminho_rel
    if not f.exists():
        sys.exit(f"ERRO: imagem não encontrada: {f}")
    mime = mimetypes.guess_type(f.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()

def atualizar_service_worker(html: str) -> None:
    """Troca a versao do cache pro tablet nao servir o app antigo."""
    sw = RAIZ / "service-worker.js"
    if not sw.exists():
        return
    versao = hashlib.md5(html.encode()).hexdigest()[:10]
    texto = re.sub(r"const CACHE='[^']*'",
                   f"const CACHE='kavuka-conarh-{versao}'",
                   sw.read_text(encoding="utf-8"))
    sw.write_text(texto, encoding="utf-8")
    print(f"service-worker.js -> cache kavuka-conarh-{versao}")


def main():
    dev = "--dev" in sys.argv
    html = (SRC / "app.html").read_text(encoding="utf-8")
    vagas = json.loads((SRC / "jobs.json").read_text(encoding="utf-8"))

    # no modo --dev as imagens ficam soltas (abre rapido); no normal, embutidas
    img = (lambda caminho: caminho) if dev else embutir

    for vaga in vagas:
        vaga["icon"] = img(vaga["icon"])
        for cand in vaga["cands"]:
            cand["img"] = img(cand["img"])

    html = html.replace("{{LOGO}}",   img("img/logo.png"))
    html = html.replace("{{MASCOT}}", img("img/mascot.png"))
    html = html.replace("{{CLAW}}",   img("img/claw.png"))
    html = html.replace("{{JOBS}}",
        "const JOBS = " + json.dumps(vagas, ensure_ascii=False) + ";")

    if "{{" in html:
        sys.exit("ERRO: sobrou um marcador {{...}} sem substituir no app.html")

    if dev:
        saida = SRC / "dev.html"
        saida.write_text(html, encoding="utf-8")
        print(f"src/dev.html gerado (preview leve) — abra no navegador")
        return

    saida = RAIZ / "index.html"
    saida.write_text(html, encoding="utf-8")
    atualizar_service_worker(html)
    print(f"index.html gerado — {saida.stat().st_size/1024/1024:.1f} MB, "
          f"{len(vagas)} vagas, {sum(len(v['cands']) for v in vagas)} candidatos")

if __name__ == "__main__":
    main()
