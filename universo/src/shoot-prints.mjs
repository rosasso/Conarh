/**
 * Recaptura os prints dos ambientes usados na apresentação.
 *
 * PRECISA de uma instância LOCAL do kavukaexperts (rh-experts) rodando na 3355
 * contra o banco de DEMONSTRAÇÃO — nunca contra o banco real (LGPD).
 * Ver a seção "Como refazer os prints" no LEIA-ME.txt.
 *
 * Uso:  node src/shoot-prints.mjs      (precisa de playwright-core instalado)
 * Saída: PNGs 2880x1800 em ./env — depois converter com sips e rodar src/build.py
 */
import { chromium } from 'playwright-core';
import fs from 'node:fs';

const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = 'http://localhost:3355';
const OUT = '/private/tmp/claude-501/-Users-sasso/6126929a-c7be-4843-96e1-ad63449c585b/scratchpad/env';
fs.mkdirSync(OUT, { recursive: true });

// esconde o indicador de dev do Next (aparece como bolinha "N" no canto)
const HIDE_DEV = `
  nextjs-portal, [data-nextjs-dev-tools-button], #__next-build-watcher,
  [data-nextjs-toast], [data-next-badge-root] { display: none !important; }
`;

// troca o host de dev pelo dominio real do produto no texto visivel
async function fixHost(page, real) {
  await page.evaluate((realHost) => {
    const walk = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const hits = [];
    while (walk.nextNode()) {
      if (walk.currentNode.nodeValue && walk.currentNode.nodeValue.includes('localhost:3355')) hits.push(walk.currentNode);
    }
    hits.forEach(n => { n.nodeValue = n.nodeValue.replaceAll('localhost:3355', realHost); });
  }, real);
}

const browser = await chromium.launch({ executablePath: CHROME, headless: true });

async function ctx() {
  const c = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, locale: 'pt-BR' });
  await c.addStyleTag ? null : null;
  return c;
}

// ---------- GESTOR ----------
const c1 = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, locale: 'pt-BR' });
const page = await c1.newPage();
await page.addStyleTag({ content: HIDE_DEV }).catch(() => {});

await page.goto(BASE + '/login', { waitUntil: 'domcontentloaded' });
await page.waitForTimeout(1200);
await page.fill('input[type="email"], input[name="email"]', 'rodrigo.sasso@guep.com.br');
await page.fill('input[type="password"], input[name="password"]', 'kavuka2026');
await Promise.all([
  page.waitForURL(u => !String(u).includes('/login'), { timeout: 30000 }).catch(() => {}),
  page.click('button[type="submit"]'),
]);
await page.waitForTimeout(2200);
for (const sel of ['text=Pular', 'button:has-text("Pular")']) {
  try { const el = page.locator(sel).first(); if (await el.count()) { await el.click({ timeout: 4000 }); break; } } catch {}
}
await page.waitForTimeout(1000);
console.log('login gestor ->', page.url());

const GESTOR = [
  ['g_kanban', '/kanban'],
  ['g_vaga', '/vagas/demo-job-atendente-senior'],
  ['g_ana', '/candidatos/demo-cand-ana'],
  ['g_candidatos', '/candidatos'],
  ['g_vagas', '/vagas'],
  ['g_mapa', '/mapa'],
];
for (const [n, p] of GESTOR) {
  try { await page.goto(BASE + p, { waitUntil: 'networkidle', timeout: 45000 }); } catch {}
  await page.waitForTimeout(2400);
  await page.addStyleTag({ content: HIDE_DEV }).catch(() => {});
  await fixHost(page, 'gestor.kavuka.ai');
  await page.waitForTimeout(300);
  await page.screenshot({ path: `${OUT}/${n}.png` });
  console.log('  ok', n);
}

// ---------- CANDIDATO ----------
const c2 = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2, locale: 'pt-BR' });
const p2 = await c2.newPage();
await p2.goto(BASE + '/portal/login', { waitUntil: 'domcontentloaded' });
await p2.waitForTimeout(1200);
await p2.addStyleTag({ content: HIDE_DEV }).catch(() => {});
await fixHost(p2, 'candidato.kavuka.ai');
await p2.screenshot({ path: `${OUT}/c_login.png` });
console.log('  ok c_login');

try {
  await p2.fill('input[type="email"], input[name="email"]', 'ana.carolina@email.com');
  await p2.fill('input[type="password"], input[name="password"]', 'demo2026');
  await Promise.all([
    p2.waitForURL(u => !String(u).includes('/portal/login'), { timeout: 30000 }).catch(() => {}),
    p2.click('button[type="submit"]'),
  ]);
  await p2.waitForTimeout(3000);
  console.log('login candidato ->', p2.url());
} catch (e) { console.log('login candidato falhou:', e.message); }

const CAND = [
  ['c_me', '/portal/me'],
  ['c_kyid', '/kyid/demo-ana-carolina-kyid-token-2026-kavuka'],
];
for (const [n, p] of CAND) {
  try { await p2.goto(BASE + p, { waitUntil: 'networkidle', timeout: 45000 }); } catch {}
  await p2.waitForTimeout(2600);
  await p2.addStyleTag({ content: HIDE_DEV }).catch(() => {});
  await fixHost(p2, 'candidato.kavuka.ai');
  await p2.waitForTimeout(300);
  await p2.screenshot({ path: `${OUT}/${n}.png` });
  console.log('  ok', n);
}

// KYID: segunda dobra (Big Five) para um print extra
try {
  await p2.evaluate(() => window.scrollBy(0, 1150));
  await p2.waitForTimeout(1400);
  await p2.screenshot({ path: `${OUT}/c_kyid2.png` });
  console.log('  ok c_kyid2');
} catch {}

await browser.close();
console.log('fim');
