const {test,expect}=require('@playwright/test');
const fs=require('node:fs');
const order=['aliveness','fidelity','expression','release'];
const key='ways.home.returning.v1';
const legacy={version:1,language:'acim',fields:{situation:'旧版的一件事',aliveness:'原来的热爱',expression:'原来的表达',fidelity:'原来的聆听',release:'原来的松开',action:'一小步',boundary:'保留边界',review:'周末复看'}};

test('shared grounding and reordered practices preserve stable identities',async({page})=>{
  await page.goto('returning.html');
  await expect(page.locator('.return-support-grid article')).toHaveCount(4);
  await expect(page.locator('.return-fruit-grid article')).toHaveCount(4);
  expect(await page.locator('.return-map a').evaluateAll(xs=>xs.map(x=>x.hash.replace('#lens-','')))).toEqual(order);
  await expect(page.locator('#four-practices')).toContainText('不是修行等级');
  await expect(page.locator('#integration')).toContainText('不是修行评分表');
  await page.goto('returning/explore.html');
  expect(await page.locator('[data-reflection]').evaluateAll(xs=>xs.map(x=>x.dataset.reflection))).toEqual(order);
  await expect(page.locator('#grounding')).toContainText('不会被存储');
  await expect(page.locator('[data-return-field]')).toHaveCount(8);
});

test('ACIM is a distinct sourced perspective with examples rather than a higher rank',async({page})=>{
  await page.goto('returning.html');
  await page.locator('#purpose-not-status a').click();
  await expect(page).toHaveURL(/returning\/acim.html$/);
  await expect(page.locator('.acim-orientation')).toContainText('不代表所有灵修传统');
  await expect(page.locator('.acim-section')).toHaveCount(8);
  await expect(page.locator('.purpose-row')).toHaveCount(4);
  await expect(page.locator('.acim-practice-grid article')).toHaveCount(4);
  await expect(page.locator('.acim-case')).toHaveCount(3);
  await expect(page.locator('#acim-forgiveness')).toContainText('不要求受伤者继续接触施害者');
  await expect(page.locator('#acim-again')).toContainText('不再追加自我定罪');
  for(const s of await page.locator('.acim-section').all())expect(await s.locator('.citation').count()).toBeGreaterThan(0);
  await page.locator('.acim-case').nth(1).locator('summary').click();
  await expect(page.locator('.acim-case').nth(1)).toContainText('不是全部身份的判决');
});

test('explicit ACIM link selects its language without loading or storing a draft',async({page})=>{
  await page.goto('returning/acim.html');
  await page.locator('.acim-orientation a[href*="language=acim"]').click();
  await expect(page.locator('[name="language"][value="acim"]')).toBeChecked();
  await expect(page.locator('.acim-notebook-prompts li')).toHaveCount(4);
  await expect(page.locator('[data-release-language="acim"]')).toBeVisible();
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBeNull();
  // Only a supported value is accepted; it never becomes markup or a selector.
  await page.goto('returning/explore.html?language=invalid');
  await expect(page.locator('[name="language"][value="everyday"]')).toBeChecked();
});

test('old version-one records survive the reorder without silent migration or loss',async({page})=>{
  await page.goto('returning/explore.html');
  const raw=JSON.stringify(legacy);
  await page.evaluate(([k,v])=>localStorage.setItem(k,v),[key,raw]);
  await page.reload();
  for(const f of Object.keys(legacy.fields))await expect(page.locator(`#note-${f}`)).toHaveValue('');
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(raw);
  await page.locator('#return-restore').click();
  for(const [name,value] of Object.entries(legacy.fields))await expect(page.locator(`#note-${name}`)).toHaveValue(value);
  expect(await page.evaluate(k=>localStorage.getItem(k),key)).toBe(raw);
  await page.locator('#return-preview').click();
  const text=await page.locator('#return-card-content').textContent();
  for(const value of Object.values(legacy.fields))expect(text).toContain(value);
  const event=page.waitForEvent('download');
  await page.locator('#return-export').click();
  const exported=fs.readFileSync(await (await event).path(),'utf8');
  for(const value of Object.values(legacy.fields))expect(exported).toContain(value);
  await page.locator('#return-save').click();
  const saved=await page.evaluate(k=>JSON.parse(localStorage.getItem(k)),key);
  expect(saved).toEqual(legacy);
});

test('illustrations load, retain their credits, and use the shared image viewer',async({page})=>{
  const remote=[];
  page.on('request',r=>{if(new URL(r.url()).hostname!=='127.0.0.1')remote.push(r.url());});
  for(const [path,count] of [['returning.html',2],['returning/acim.html',1]]){
    await page.goto(path);
    await expect(page.locator('.return-artwork')).toHaveCount(count);
    for(const figure of await page.locator('.return-artwork').all()){
      await figure.scrollIntoViewIfNeeded();
      await expect.poll(()=>figure.locator('img').evaluate(i=>i.complete&&i.naturalWidth>100)).toBe(true);
      await expect(figure.locator('.image-credit')).toContainText('Public Domain');
      await expect(figure.locator('figcaption')).toContainText('本站的观看邀请');
      await figure.locator('[data-lightbox]').click();
      await expect(page.locator('#image-dialog')).toBeVisible();
      await expect(page.locator('#large-image-caption')).toContainText('使用依据');
      await page.keyboard.press('Escape');
    }
  }
  expect(remote).toEqual([]);
});

test('updated pages and opt-in theological text remain readable without scripts',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const p=await context.newPage();
  await p.goto('http://127.0.0.1:8785/ways.home/returning/acim.html');
  await expect(p.locator('.acim-section')).toHaveCount(8);
  await expect(p.locator('.purpose-row')).toHaveCount(4);
  await p.locator('.acim-case').first().locator('summary').click();
  await expect(p.locator('.acim-case').first().locator('dl')).toBeVisible();
  await p.goto('http://127.0.0.1:8785/ways.home/returning/explore.html');
  await p.locator('[data-release-language="acim"] summary').click();
  await expect(p.locator('.acim-notebook-prompts')).toBeVisible();
  await expect(p.locator('#note-release')).toBeEditable();
  await context.close();
});

test('visual review: grounding, path diagram, artwork, purpose and mobile reading',async({page})=>{
  for(const width of [390,1440]){
    await page.setViewportSize({width,height:1000});
    for(const [path,selector,name] of [
      ['returning.html','#foundation','grounding'],
      ['returning.html','.return-route-diagram','route'],
      ['returning/acim.html','.acim-visual-opening','art'],
      ['returning/acim.html','.purpose-diagram','purpose']
    ]){
      await page.goto(path);
      await page.locator(selector).scrollIntoViewIfNeeded();
      expect(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)).toBeLessThanOrEqual(1);
      await page.screenshot({path:`preview-return-revision-${name}-${width}.png`});
    }
  }
});
