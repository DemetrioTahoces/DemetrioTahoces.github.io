#!/usr/bin/env node
/**
 * screenshot.mjs – Capturas de escritorio y móvil de un post (y del índice del blog).
 *
 * Requisitos: `npm ci --prefix .agents/skills/manage-blog/scripts` y un servidor
 * estático en la raíz del repo (`python -m http.server 8000`).
 *
 * Uso:
 *   node .agents/skills/manage-blog/scripts/screenshot.mjs <slug> [directorio-salida] [url-base]
 *
 * Informa de desbordamiento horizontal y de recursos que no cargan. Si Tailwind o
 * Google Fonts no cargan (red bloqueada), las capturas no reflejan la web real.
 */

import puppeteer from 'puppeteer-core';
import { existsSync, mkdirSync } from 'node:fs';
import { join, resolve } from 'node:path';

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium',
    join(process.env.PLAYWRIGHT_BROWSERS_PATH || '/opt/pw-browsers', 'chromium'),
  ].filter(Boolean);
  const found = candidates.find((p) => existsSync(p));
  if (!found) {
    console.error('Chrome no encontrado. Instálalo o define CHROME_PATH.');
    process.exit(1);
  }
  return found;
}

const [,, slug, outArg = 'blog-screenshots', base = 'http://localhost:8000'] = process.argv;
if (!slug) {
  console.error('Uso: node screenshot.mjs <slug> [directorio-salida] [url-base]');
  process.exit(1);
}

const outDir = resolve(outArg);
mkdirSync(outDir, { recursive: true });

const targets = [
  ['post-escritorio', `blog/posts/${slug}.html`, 1280],
  ['post-movil', `blog/posts/${slug}.html`, 390],
  ['indice-escritorio', 'blog/index.html', 1280],
  ['indice-movil', 'blog/index.html', 390],
];

const browser = await puppeteer.launch({
  headless: true,
  executablePath: findChrome(),
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

let problems = 0;
for (const [name, path, width] of targets) {
  const page = await browser.newPage();
  const failed = [];
  page.on('requestfailed', (request) => failed.push(request.url()));
  page.on('response', (response) => { if (response.status() >= 400) failed.push(`${response.status()} ${response.url()}`); });
  // Sin animaciones: todo el contenido visible desde el principio.
  await page.emulateMediaFeatures([{ name: 'prefers-reduced-motion', value: 'reduce' }]);
  await page.setViewport({ width, height: 900 });
  await page.goto(`${base}/${path}`, { waitUntil: 'networkidle0', timeout: 30000 });
  const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  const file = join(outDir, `${slug}-${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  const overflow = scrollWidth > width;
  console.log(`${overflow ? 'AVISO' : 'OK   '} ${name}: ${file}${overflow ? ` (desborda: ${scrollWidth}px en ${width}px)` : ''}`);
  for (const url of failed) console.log(`      no cargó: ${url}`);
  problems += Number(overflow) + failed.length;
  await page.close();
}
await browser.close();

if (problems) {
  console.log('Revisa los avisos. Si lo que no carga es Tailwind o Google Fonts, repite las capturas con red abierta antes de sacar conclusiones.');
}
