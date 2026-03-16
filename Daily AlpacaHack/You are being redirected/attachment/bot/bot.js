import puppeteer from "puppeteer";

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const FLAG = process.env.FLAG ?? "Alpaca{REDACTED}";
const APP_URL = process.env.APP_URL ?? "http://localhost/";

export const visit = async (url) => {
  console.log(`Start visiting: ${url} ${new URL(APP_URL).origin}`);

  const browser = await puppeteer.launch({
    headless: "new",
    pipe: true,
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage",
      "--disable-gpu",
      '--js-flags="--noexpose_wasm"',
    ],
  });

  try {
    const page = await browser.newPage();
    await page.setCookie({
      name: "FLAG",
      value: FLAG,
      domain: new URL(APP_URL).hostname,
      path: "/",
    });
    await page.goto(url, { timeout: 5000 });
    await sleep(5000);
    await page.close();
  } catch (e) {
    console.error(e);
  }

  await browser.close();

  console.log(`End visiting: ${url}`);
};