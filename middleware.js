// Protótipo: acesso só para a equipe (senha única, HTTP Basic).
// A senha fica na variável de ambiente PAINEL_SENHA da Vercel — nunca no código.
// Sem a variável configurada, o site fica fechado (falha segura).
import { next } from '@vercel/functions';

export const config = { runtime: 'edge' };

function negar(msg) {
  return new Response(msg, {
    status: 401,
    headers: {
      'WWW-Authenticate': 'Basic realm="Prototipo - acesso restrito a equipe", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
      'X-Robots-Tag': 'noindex, nofollow',
    },
  });
}

function iguais(a, b) {
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export default function middleware(request) {
  const senha = process.env.PAINEL_SENHA;
  if (!senha) return negar('Protótipo em teste: acesso restrito à equipe. (Senha ainda não configurada.)');
  const auth = request.headers.get('authorization') || '';
  if (auth.startsWith('Basic ')) {
    try {
      const txt = new TextDecoder().decode(Uint8Array.from(atob(auth.slice(6)), c => c.charCodeAt(0)));
      const dada = txt.slice(txt.indexOf(':') + 1);
      if (iguais(dada, senha)) return next({ headers: { 'X-Robots-Tag': 'noindex, nofollow', 'Cache-Control': 'private, no-store' } });
    } catch (e) {}
  }
  return negar('Protótipo em teste: acesso restrito à equipe. Digite a senha (o usuário pode ser qualquer nome).');
}
