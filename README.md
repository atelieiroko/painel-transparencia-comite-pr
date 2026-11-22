# Mapa das ações do Comitê de Cultura do Paraná

Página separada do painel de transparência (https://painel-transparencia-comite-pr.vercel.app). Mostra o Brasil inteiro e as ações por município, separadas como no painel: Ano I (2024), Ano II (2025–2026), Ano I + Ano II (validadas), Aditivo 2026 (aguardando validação) e Total.

`data/acoes-PR.json` é gerado na branch `main` por `automacao/gerar_dados_mapa.py`, a partir dos mesmos dados do painel. Na publicação, `build.mjs` baixa as malhas do IBGE (API de malhas v3). Os municípios são ligados às ações pelo código DTB/IBGE.

Codificação em estudo: o código de município (DTB/IBGE) difere da codificação do PNCC, que define códigos apenas para os estados.
