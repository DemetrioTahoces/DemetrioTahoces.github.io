#!/usr/bin/env node
/**
 * svg-to-png.mjs – Convierte SVG a PNG con fuentes web (Inter, JetBrains Mono).
 *
 * Requisito (una vez desde la raíz del repo):
 *   npm install puppeteer-core --prefix .agents/skills/manage-blog/scripts
 *
 * Uso:
 *   node .agents/skills/manage-blog/scripts/svg-to-png.mjs <entrada.svg> <salida.png> [ancho] [alto]
 *
 * Ejemplo:
 *   node .agents/skills/manage-blog/scripts/svg-to-png.mjs blog/assets/mi-diagrama.svg blog/assets/mi-diagrama-linkedin.png 1200 630
 */

import puppeteer from 'puppeteer-core';
import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

function findChrome() {
  const candidates = [
    process.env.CHROME_PATH,
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome',
    '/usr/bin/google-chrome-stable',
  ].filter(Boolean);

  for (const p of candidates) {
    if (existsSync(p)) return p;
  }
  console.error(
    'Chrome no encontrado. Instálalo o define CHROME_PATH como variable de entorno.'
  );
  process.exit(1);
}

const [,, svgPath, pngPath, widthArg = '1200', heightArg = '630'] = process.argv;

if (!svgPath || !pngPath) {
  console.error(
    'Uso: node svg-to-png.mjs <entrada.svg> <salida.png> [ancho] [alto]'
  );
  process.exit(1);
}

const width  = parseInt(widthArg, 10);
const height = parseInt(heightArg, 10);
const svgAbs = resolve(svgPath);
const pngAbs = resolve(pngPath);

if (!existsSync(svgAbs)) {
  console.error(`SVG no encontrado: ${svgAbs}`);
  process.exit(1);
}

const svgContent = readFileSync(svgAbs, 'utf-8');

const html = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { width: ${width}px; height: ${height}px; overflow: hidden; background: #030712; }
  svg  { width: 100%; height: 100%; font-family: 'Inter', system-ui, sans-serif; }
</style>
</head>
<body>${svgContent}</body>
</html>`;

const chromePath = findChrome();
console.log(`Chrome:      ${chromePath}`);
console.log(`SVG entrada: ${svgAbs}`);
console.log(`PNG salida:  ${pngAbs}  (${width}x${height} @2x)`);

const browser = await puppeteer.launch({
  headless: true,
  executablePath: chromePath,
  args: ['--no-sandbox', '--disable-setuid-sandbox'],
});

const page = await browser.newPage();
await page.setViewport({ width, height, deviceScaleFactor: 2 });
await page.setContent(html, { waitUntil: 'networkidle0' });
await page.evaluate(() => document.fonts.ready);

const body = await page.$('body');
await body.screenshot({ path: pngAbs, type: 'png' });
await browser.close();

console.log('Conversion completada.');
