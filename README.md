# Mapa das ações dos Comitês de Cultura (protótipo nacional)

Página separada do painel de transparência. Na publicação, `build.mjs` junta `data/acoes-*.json` (um arquivo por comitê) e baixa as malhas do IBGE (API de malhas v3) para os estados com ações. Os municípios são ligados às ações pelo código DTB/IBGE.

Para incluir um comitê: adicionar `data/acoes-UF.json` no mesmo formato.

Codificação em estudo: o código de município (DTB/IBGE) difere da codificação do PNCC, que define códigos apenas para os estados.
