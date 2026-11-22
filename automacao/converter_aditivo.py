"""Lê a Planilha viva do aditivo (exportada em .xlsx) e gera os registros do
aditivo no mesmo formato das ações do Ano I e II do painel.

Uso: python3 converter_aditivo.py viva.xlsx saida.json
Nada de e-mail ou nome de responsável é levado para o painel.
"""
import openpyxl, json, re, sys, datetime

src, out_path = sys.argv[1:3]
wb = openpyxl.load_workbook(src, read_only=True, data_only=True)

def s(v): return ' '.join(str(v).split()) if v is not None else ''
def d(v):
    if isinstance(v, datetime.datetime): return v.strftime('%Y-%m-%d')
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', str(v or ''))
    return f'{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}' if m else None
def horas(v):
    if isinstance(v, (int, float)): return float(v)
    t = s(v).lower().replace(',', '.')
    m = re.match(r'(\d+(?:\.\d+)?)\s*(?:h|hora|horas)?\s*(?:e\s*)?(\d+)?\s*(?:min)?', t)
    if not m: return None
    h = float(m.group(1)); mi = int(m.group(2)) if m.group(2) else 0
    return round(h + mi / 60, 2)
def num(v):
    try: return float(str(v).replace(',', '.'))
    except Exception: return None

# --- aba Ações: código, município IBGE, tipo final, observação
acoes = {}
ws = wb['Ações']; it = ws.iter_rows(values_only=True); H = [s(h) for h in next(it)]
ix = {h: i for i, h in enumerate(H)}
for r in it:
    r = list(r) + [None] * (len(H) - len(r))
    if not r[ix['Código da ação']]: continue
    acoes[s(r[ix['Código da ação']])] = dict(
        mun=s(r[ix['Município (IBGE)']]), obs=s(r[ix['Observação']]),
        tipo=s(r[ix['Tipo (ajuste)']]) or s(r[ix['Tipo']]), osc=s(r[ix['OSC']]))

# --- aba Documentos: links originais por sigla
docs = {}
ws = wb['Documentos']; it = ws.iter_rows(values_only=True); H = [s(h) for h in next(it)]
ix = {h: i for i, h in enumerate(H)}
for r in it:
    r = list(r) + [None] * (len(H) - len(r))
    cod = s(r[ix['Código da ação']]); link = s(r[ix['Link original']])
    if cod and link.startswith('http'):
        docs.setdefault(cod, {}).setdefault(s(r[ix['Sigla']]), []).append(link)

# --- respostas do formulário
ws = wb['Respostas (espelho)']; it = ws.iter_rows(values_only=True); H = [s(h) for h in next(it)]
def col(prefix, n=0):
    hits = [i for i, h in enumerate(H) if h.lower().startswith(prefix.lower())]
    return hits[n]
C = dict(cod=col('Código da ação'), carimbo=col('Carimbo'), osc=col('OSC'), nome=col('Nome a ação'),
         evento=col('Se sim, qual o nome do evento'), ini=col('Data de início'), fim=col('Data de finalização'),
         carga=col('Carga Horária'), local=col('Localidade'), parc=col('Se sim, liste os parceiros'),
         gpte=col('A ação teve como público-alvo'), part=col('Quantidade de participantes'),
         rip=col('A ação ocorreu ou foi voltada especificamente'), eixo=col('Selecione o Eixo'),
         ling=col('Marque os tipos e linguagens'))
SC = [i for i, h in enumerate(H) if h.startswith('Houve ação cultural')]
TEMAS = [i for i, h in enumerate(H) if h.startswith('Selecione o tema')]
OSCN = {'Soylocoporti': ('Coletivo Soylocoporti', 'Coletivo Soylocoporti – Pela Integração Latinoamericana'),
        'CEAGRO': ('CEAGRO', 'CEAGRO – Centro de Desenvolvimento Sustentável e Capacitação em Agroecologia'),
        'Instituto Cidadania': ('Instituto Cidadania', 'Instituto Cidadania')}
TIPO = {'FOR': 'Formação', 'MOB': 'Mobilização', 'COM': 'Comunicação'}
LING = [('Música','Música'),('Culturas Tradicionais','Culturas tradicionais e populares'),('Dança','Dança'),('Artes de Rua','Artes de rua'),('Circ','Artes circenses'),('Artes Visuais','Artes visuais'),('Teatro','Teatro / performance'),('Artes Integradas','Artes integradas'),('Hip','Hip-hop'),('Audiovisual','Audiovisual'),('Literatura','Literatura'),('Artesanato','Artesanato')]

out, rel, fora = [], [], set()
for r in it:
    r = list(r) + [None] * (len(H) - len(r))
    cod = s(r[C['cod']])
    if not cod: continue
    a = acoes.get(cod, {}); dc = docs.get(cod, {})
    mun = a.get('mun', '')
    if mun.startswith('Remota') or not mun: muns = []
    else: muns = [mun]
    if 'fora do' in a.get('obs', '').lower(): fora.add(mun)
    osc_k = next((k for k in OSCN if k.lower() in s(r[C['osc']]).lower()), None)
    osc, osc_nome = OSCN.get(osc_k, ('Não identificada', ''))
    gp = s(r[C['gpte']])
    sc = 'Sim' if any(s(r[i]).startswith('Sim') for i in SC) else ('Não' if any(s(r[i]) for i in SC) else None)
    lt = s(r[C['ling']]).lower()
    carga = horas(r[C['carga']])
    if carga is None: rel.append(f'[carga não lida] {cod}: "{s(r[C["carga"]])}"')
    part = num(r[C['part']])
    if part is None: rel.append(f'[público ausente] {cod}')
    ini, fim = d(r[C['ini']]), d(r[C['fim']])
    if ini and fim and fim < ini: rel.append(f'[fim antes do início] {cod}'); fim = ini
    temas = '; '.join(s(r[i]) for i in TEMAS if s(r[i]))
    rip = s(r[C['rip']])
    out.append(dict(
        id=cod, codigo=cod, bloco='Aditivo', periodo='Aditivo',
        status='Registrada – aguardando validação', ressalva=False, diligencia=False,
        enviado=d(r[C['carimbo']]) and '/'.join(reversed(d(r[C['carimbo']]).split('-'))),
        tipo=TIPO.get(a.get('tipo', 'FOR'), 'Formação'), meta='', executora='',
        osc=osc, osc_nome=osc_nome, nome=s(r[C['nome']]), inicio=ini, fim=fim,
        formato='Remota' if not muns else None, carga=carga,
        municipio=muns[0] if muns else 'Remota (sem município)', municipios=muns,
        municipio_obs=('Município fora do Paraná.' if mun in fora else None),
        local=s(r[C['local']]), parceiros=s(r[C['parc']]), tipos_parceiros='',
        gpte=[] if (not gp or 'não teve' in gp) else [g.strip() for g in re.split(r',\s*(?=[A-ZÁÉÍÓÚ])', gp)],
        editais=None, porte=None, participantes=part,
        eixo=s(r[C['eixo']]) or None, temas=temas or None, evento=s(r[C['evento']]) or None,
        regiao_prioritaria=None if rip.upper() in ('', 'NÃO', 'NAO') else rip,
        fotos=dc.get('FOT', []), lista=dc.get('LST', []) + dc.get('LDG', []), divulgacao=dc.get('DIV', []),
        fotos_sc=dc.get('FSC', []), ementa=dc.get('EME', []), material=dc.get('MAT', []),
        com_anexo=[], com_links=[], sociocultural=sc,
        linguagens=[v for k, v in LING if k.lower() in lt]))
    if not dc.get('LST') and not dc.get('LDG'): rel.append(f'[sem lista de presença] {cod}')

json.dump({'acoes': out, 'fora_uf': sorted(fora), 'relatorio': rel}, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'ações do aditivo;', 'fora da UF:', sorted(fora))
print('\n'.join(rel) or 'sem inconsistências')
