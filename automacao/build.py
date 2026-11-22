"""Monta o index.html do painel: Ano I e II (fixo, validado) + Aditivo (planilha viva).
Uso: python3 build.py aditivo.json "dd/mm/aaaa hh:mm" index.html
"""
import json, sys
adt_path, quando, saida = sys.argv[1:4]
base = json.load(open('ano12.json', encoding='utf-8'))
adt = json.load(open(adt_path, encoding='utf-8'))
meta = {'verificado_em': quando, 'n': len(adt['acoes']), 'fora_uf': adt['fora_uf']}
js = ('window.ACOES=' + json.dumps(base + adt['acoes'], ensure_ascii=False, separators=(',', ':')) + ';\n'
      'window.META_ADITIVO=' + json.dumps(meta, ensure_ascii=False) + ';')
t = open('template.html', encoding='utf-8').read()
open(saida, 'w', encoding='utf-8').write(t.replace('__DATA__', js))
print('ok', len(base), 'Ano I e II +', len(adt['acoes']), 'aditivo')
