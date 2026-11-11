/**
 * Realtime capture of the Three.js story as MP4 via Playwright video + ffmpeg remux.
 * Usage: npm run capture
 */
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { createServer } from "vite";
import path from "node:path";
import fs from "node:fs";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const webRoot = path.resolve(__dirname, "..");
const outDir = path.resolve(webRoot, "../exports/final");
const width = 1280;
const height = 720;
const durationMs = 76_000;

fs.mkdirSync(outDir, { recursive: true });

const server = await createServer({
  root: webRoot,
  server: { port: 5179, host: "127.0.0.1", strictPort: true },
  configFile: path.join(webRoot, "vite.config.js"),
});
await server.listen();
console.log("preview server ready");

const browser = await chromium.launch({
  headless: true,
  args: ["--use-gl=angle", "--use-angle=swiftshader"],
});

const context = await browser.newContext({
  viewport: { width, height },
  deviceScaleFactor: 1,
  recordVideo: { dir: outDir, size: { width, height } },
});
const page = await context.newPage();
page.on("pageerror", (e) => console.error("PAGEERROR", e.message));

await page.goto("http://127.0.0.1:5179/?capture=1", { waitUntil: "networkidle" });
await page.waitForFunction(() => window.__neuronFactory);
await page.evaluate(() => {
  window.__neuronFactory.seekTo(0);
  window.__neuronFactory.play();
});
console.log("recording 75s playback...");
await page.waitForTimeout(durationMs);
await page.evaluate(() => window.__neuronFactory.pause());

const video = page.video();
await page.close();
const webmPath = await video.path();
await context.close();
await browser.close();
await server.close();

const mp4 = path.join(outDir, "neuron_factory.mp4");
console.log("remux", webmPath, "->", mp4);
const ff = spawn(
  "ffmpeg",
  ["-y", "-i", webmPath, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", mp4],
  { stdio: "inherit" }
);
await new Promise((resolve, reject) => {
  ff.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg ${code}`))));
});

// keep a couple stills for docs
fs.copyFileSync(webmPath, path.join(outDir, "neuron_factory_raw.webm"));
console.log(`Wrote ${mp4}`);
