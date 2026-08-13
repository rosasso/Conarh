#!/bin/bash
# Sobe os DOIS apps no mesmo endereço (localhost) — é isso que faz o hub
# conseguir repetir o cadastro feito no quiz (o navegador só compartilha o
# armazenamento entre páginas do MESMO endereço).
#
#   quiz da capivara :  http://localhost:8787/
#   hub (Universo)   :  http://localhost:8787/universo/
#
# Feche esta janela para parar o servidor.
cd "$(dirname "$0")"
echo "Kavuka — quiz:  http://localhost:8787/"
echo "Kavuka — hub :  http://localhost:8787/universo/"
echo
open "http://localhost:8787/"
python3 -m http.server 8787
