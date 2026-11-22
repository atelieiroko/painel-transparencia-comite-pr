"""Gera data/acoes-PR.json do Mapa das ações a partir dos mesmos dados do painel.

Uso: python3 gerar_dados_mapa.py ano12.json aditivo.json mun_ibge.json saida.json

- ano12.json: ações validadas do Ano I e II (com o campo periodo = 'Ano I' ou 'Ano II').
- aditivo.json: saída de converter_aditivo.py (periodo = 'Aditivo').
- mun_ibge.json: nome do município -> código DTB/IBGE de 7 dígitos (lista fixa do Ano I e II).
  Nas ações do aditivo o código vem do próprio código da ação (PR-A0000-TIP-<IBGE>-AAAAMM).
Nada de e-mail, nome de responsável ou link de documento vai para o mapa.
"""
import json, sys

ano12, adt, munf, saida = sys.argv[1:5]
A = json.load(open(ano12, encoding='utf-8'))
D = json.load(open(adt, encoding='utf-8'))
MUN = json.load(open(munf, encoding='utf-8'))
out, faltam = [], set()

def reg(a, muns):
    return dict(id=a['id'], codigo=a.get('codigo'), comite='PR', nome=a['nome'], tipo=a['tipo'], osc=a['osc'],
                inicio=a.get('inicio'), participantes=a.get('participantes'), formato=a.get('formato'),
                status=a['status'], periodo=a['periodo'], bloco=a['bloco'],
                sociocultural=a.get('sociocultural'), carga=a.get('carga'), municipios=muns)

for a in A:
    muns = []
    for n in a['municipios']:
        c = MUN.get(n)
        if c: muns.append({'n': n, 'c': c})
        else: faltam.add(n)
    out.append(reg(a, muns))

for a in D['acoes']:
    cod = (a.get('codigo') or '').split('-')
    ibge = cod[3] if len(cod) > 3 else ''
    muns = []
    if a['municipios'] and ibge.isdigit() and len(ibge) == 7 and ibge not in ('0000000', '9999999'):
        n = a['municipios'][0]
        muns = [{'n': n, 'c': ibge}]
        MUN.setdefault(n, ibge)
    elif a['municipios']:
        n = a['municipios'][0]
        if MUN.get(n): muns = [{'n': n, 'c': MUN[n]}]
        else: faltam.add(n)
    out.append(reg(a, muns))

json.dump(out, open(saida, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'ações no mapa;', sum(1 for x in out if not x['municipios']), 'sem município (remotas)')
if faltam: print('ATENÇÃO, municípios sem código IBGE:', ', '.join(sorted(faltam)))
