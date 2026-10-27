// ブラウザでツールを開き、sample のCSVとひな形を読み込ませて、出力Excelを output/ に保存する
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");

const ROOT = path.join(__dirname, "..");
const HTML = path.join(ROOT, "脱脂内示データ抽出.html");
const SAMPLE = path.join(ROOT, "sample");

(async () => {
  const files = fs.readdirSync(SAMPLE)
    .filter(f => f.endsWith(".csv") || (f.endsWith(".xlsx") && !f.startsWith("期待結果")))
    .map(f => ({ name: f, mimeType: "application/octet-stream", buffer: fs.readFileSync(path.join(SAMPLE, f)) }));

  const browser = await chromium.launch();
  const page = await browser.newPage({ acceptDownloads: true, viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));

  await page.goto(pathToFileURL(HTML).href);
  await page.setInputFiles("#file", files);
  await page.waitForSelector("#dl:not([disabled])", { timeout: 15000 });

  const tiles = await page.$$eval(".tile .n", els => els.map(e => e.textContent));
  console.log(`背番 ${tiles[0]} / 一致 ${tiles[1]} / 注意 ${tiles[2]} / 異常 ${tiles[3]}`);
  const alarm = (await page.textContent("#alarm")).trim();
  if (alarm) console.log("画面の警告:", alarm);

  fs.mkdirSync(path.join(ROOT, "output"), { recursive: true });
  await page.screenshot({ path: path.join(ROOT, "output", "screen.png") });
  const [dl] = await Promise.all([page.waitForEvent("download"), page.click("#dl")]);
  // ヘッドレス環境では日本語のファイル名が取れないことがあるので固定名で保存
  const out = path.join(ROOT, "output", "test_output.xlsx");
  await dl.saveAs(out);
  console.log("保存:", out);

  await browser.close();
  if (errors.length) { console.error("JSエラー:", errors); process.exit(1); }
})();
