const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  
  // Set a reasonable viewport to capture the full widget nicely
  await page.setViewportSize({ width: 900, height: 1200 });
  
  // Use the raw GitHub URL to your widget.html (adjust username/repo/branch if needed)
  await page.goto('https://raw.githubusercontent.com/SERGIOSCAR/punta-indio-dashboard/main/widget.html', {
    waitUntil: 'networkidle',
    timeout: 60000
  });
  
  // Give Windguru extra time to load data (async fetches, charts, etc.)
  await page.waitForTimeout(10000);  // 10 seconds; increase to 15000 if still blank/incomplete
  
  // Optional: wait for a specific element that appears when loaded (inspect the widget in browser)
  // await page.waitForSelector('.wgfcst', { timeout: 30000 });  // example selector – uncomment & adjust
  
  await page.screenshot({
    path: 'windguru-widget.png',
    fullPage: false  // set true if you want the entire scrollable content
  });
  
  await browser.close();
})();
