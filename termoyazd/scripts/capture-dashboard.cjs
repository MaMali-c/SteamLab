const {chromium}=require(process.env.TERMOYAZD_PLAYWRIGHT);
const fs=require('node:fs');
(async()=>{
 fs.mkdirSync('termoyazd/docs/images',{recursive:true});
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1536,height:1120},deviceScaleFactor:1});
  await page.goto('http://127.0.0.1:4173',{waitUntil:'networkidle'});
  await page.locator('#input-T').fill('300');
  await page.locator('#input-P').fill('500');
  await page.getByRole('button',{name:/Calculate/}).click();
  await page.getByText('CALCULATION COMPLETE',{exact:true}).waitFor({timeout:180000});
  await page.getByRole('article',{name:'Specific enthalpy result'}).getByText(/3,?064\.5962/).waitFor();
  await page.waitForTimeout(1500);
  await page.screenshot({path:'termoyazd/docs/images/dashboard-desktop.png'});
  await page.setViewportSize({width:390,height:1000});
  await page.waitForTimeout(800);
  await page.screenshot({path:'termoyazd/docs/images/dashboard-mobile.png',fullPage:true});
  console.log('Captured real desktop and mobile layouts after a successful IF97 calculation.');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
