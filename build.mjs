// Build do Mapa das Ações dos Comitês de Cultura.
// Roda na Vercel a cada publicação: junta os arquivos data/acoes-*.json e data/comites.json e baixa
// as malhas oficiais do IBGE (API de malhas v3) só para os estados com ações.
// Os municípios são ligados às ações pelo código DTB/IBGE de 7 dígitos.
import { readFile, writeFile, mkdir, copyFile, readdir } from 'node:fs/promises';

const BASE = 'https://servicodados.ibge.gov.br/api/v3/malhas';
const GEO = 'formato=application/vnd.geo%2Bjson&qualidade=minima';
const OUT = 'public';

async function get(url) {
  for (let i = 0; i < 4; i++) {
    try {
      const r = await fetch(url, { headers: { Accept: 'application/json' } });
      if (!r.ok) throw new Error(`HTTP ${r.status} em ${url}`);
      return await r.json();
    } catch (e) {
      if (i === 3) throw e;
      console.log(`Tentativa ${i + 1} falhou (${e.message}); tentando de novo...`);
      await new Promise(s => setTimeout(s, 3000 * (i + 1)));
    }
  }
}

const rnd = n => Math.round(n * 1000) / 1000;
const roundGeom = g => {
  const r = c => (typeof c[0] === 'number' ? [rnd(c[0]), rnd(c[1])] : c.map(r));
  return { type: g.type, coordinates: r(g.coordinates) };
};
function ringArea(ring) {
  let a = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) a += ring[j][0] * ring[i][1] - ring[i][0] * ring[j][1];
  return a / 2;
}
function ringCentroid(ring) {
  let a = 0, x = 0, y = 0;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const f = ring[j][0] * ring[i][1] - ring[i][0] * ring[j][1];
    a += f; x += (ring[j][0] + ring[i][0]) * f; y += (ring[j][1] + ring[i][1]) * f;
  }
  a /= 2;
  return a ? [rnd(x / (6 * a)), rnd(y / (6 * a))] : ring[0];
}
function centroid(g) {
  const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
  let best = null, bestA = -1;
  for (const p of polys) { const a = Math.abs(ringArea(p[0])); if (a > bestA) { bestA = a; best = p[0]; } }
  return ringCentroid(best);
}

await mkdir(`${OUT}/data`, { recursive: true });
await mkdir(`${OUT}/geo`, { recursive: true });

// 1. Ações de todos os comitês
const acoes = [];
for (const f of (await readdir('data')).filter(f => /^acoes-.*\.json$/.test(f)).sort()) {
  const arr = JSON.parse(await readFile(`data/${f}`, 'utf-8'));
  console.log(`${f}: ${arr.length} ações`);
  acoes.push(...arr);
}
await writeFile(`${OUT}/data/acoes.json`, JSON.stringify(acoes));

// 1b. Comitês (Termos de Colaboração): sede da OSC celebrante e OSCs parceiras
let comites = [];
try { comites = JSON.parse(await readFile('data/comites.json', 'utf-8')); } catch (e) { console.log('Sem data/comites.json'); }
await writeFile(`${OUT}/data/comites.json`, JSON.stringify(comites));
const codComites = new Set();
comites.forEach(c => { if (c.sede && c.sede.c) codComites.add(c.sede.c); c.parceiras.forEach(p => { if (p.mun && p.mun.c) codComites.add(p.mun.c); }); });
console.log(`Comitês: ${comites.length}, municípios de sede ou parceira: ${codComites.size}`);

// 2. Estados (Brasil inteiro)
const br = await get(`${BASE}/paises/BR?${GEO}&intrarregiao=UF`);
const ufs = br.features.map(f => ({ c: f.properties.codarea, g: roundGeom(f.geometry) }));
await writeFile(`${OUT}/geo/ufs.json`, JSON.stringify(ufs));
console.log(`Estados: ${ufs.length}`);

// 3. Municípios dos estados que têm ações (código UF = 2 primeiros dígitos do código DTB)
const codes = new Set(acoes.flatMap(a => a.municipios.map(m => m.c)));
const ufCodes = [...new Set([...codes].map(c => c.slice(0, 2)))].sort();
const ufBaixar = [...new Set([...codes, ...codComites].map(c => c.slice(0, 2)))].sort();
const centroides = {};
for (const uf of ufBaixar) {
  const fc = await get(`${BASE}/estados/${uf}?${GEO}&intrarregiao=municipio`);
  const mun = fc.features.map(f => {
    const g = roundGeom(f.geometry);
    const c = centroid(g);
    centroides[f.properties.codarea] = c;
    return { c: f.properties.codarea, g, p: c };
  });
  if (ufCodes.includes(uf)) await writeFile(`${OUT}/geo/mun-${uf}.json`, JSON.stringify(mun));
  console.log(`UF ${uf}: ${mun.length} municípios`);
}
const faltando = [...codes, ...codComites].filter(c => !centroides[c]);
if (faltando.length) throw new Error('Códigos sem malha no IBGE: ' + faltando.join(', '));
const usados = Object.fromEntries([...codes, ...codComites].map(c => [c, centroides[c]]));
await writeFile(`${OUT}/geo/centroides.json`, JSON.stringify(usados));
await writeFile(`${OUT}/geo/meta.json`, JSON.stringify({ ufs: ufCodes, gerado: new Date().toISOString(), fonte: `${BASE} (qualidade mínima)` }));

await copyFile('src/index.html', `${OUT}/index.html`);
console.log(`Pronto: ${acoes.length} ações, ${codes.size} municípios com ação, ${ufCodes.length} UFs com malha municipal.`);
