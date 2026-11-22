# Painel de Transparência — Rev.0C — Comitê de Cultura do Paraná (PNCC)

Esta branch (`main`) é a **Rev.0C**, a revisão atual do Portal da Transparência do Comitê de Cultura do Paraná.

- Painel: https://painel-transparencia-comite-pr.vercel.app
- Mapa das ações: https://mapa-acoes-comites-cultura.vercel.app (código na branch `mapa`)
- Repositório: https://github.com/atelieiroko/painel-transparencia-comite-pr

## O que tem na Rev.0C

- Abas e filtro de período: Ano I (2024) · Ano II (2025–2026) · Ano I + Ano II (validadas) · Aditivo 2026 (aguardando validação) · Total.
- Quadro "Ano I, Ano II e somatória" no Resumo.
- Fotos pelas cópias codificadas do backup (`PR-A0000-TIP-IBGE-AAAAMM_FOTnnn`); abrir uma ação direto com `#código` no endereço.
- Aditivo 2026 separado dos totais validados, atualizado todo dia às 22h30 (horário de Brasília) a partir da planilha viva.
- Botão "Veja as ações no mapa".

## Arquivos

- `index.html`: o painel publicado (arquivo único, dados embutidos).
- `automacao/`: `template.html`, `ano12.json` (Ano I e II validados), `converter_aditivo.py`, `build.py`, `gerar_dados_mapa.py`, `mun_ibge.json`, `backup.json`.

## Revisões anteriores

- Rev.0B (codificação): branch `rev0b`.
- Versão nacional dos 27 comitês: branch `rev0c` (protótipo anterior; a Rev.0C oficial é esta branch `main`).

Dados sensíveis (e-mails, nomes de responsáveis, comentários internos da conferência) não são publicados.
