import puppeteer from "puppeteer";

const sleep = async (ms) => new Promise((resolve) => setTimeout(resolve, ms));
const FLAG = process.env.FLAG ?? "Alpaca{DUMMY}";
export const APP_URL = process.env.APP_URL ?? "http://localhost:3000/";

export const visit = async (url) => {
  console.log(`Start visiting: ${url}`);

  const browser = await puppeteer.launch({
    headless: "new",
    pipe: true,
    executablePath: "/usr/bin/chromium",
    args: [
      "--no-sandbox",
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
    await page.waitForFunction(
      () => {
        const el = document.getElementById("my-uuid");
        return el && el.textContent.trim().length > 0;
      }
    );
    const uuid = (await page.$eval(`#my-uuid`, el => el.textContent)).slice(9);
    (async () => {
      await sleep(10000);
      try {
        await page.close();
        await browser.close();

        console.log(`End visiting: ${url}`);
      } catch (e) {
        console.error(e);
      }
    })();

    return `Bot is waiting with UUID: ${uuid}`
    
  } catch (e) {
    console.error(e);
  }
};
