const {test,expect}=require('@playwright/test');
const fs=require('node:fs');
const data=JSON.parse(fs.readFileSync('content/returning.json','utf8'));
const key='ways.home.returning.v1';

test('return module keeps the manifesto and distinguishes source from application',async({page})=>{
  await page.goto('returning.html');
  await expect(page.locator('.return-purpose blockquote')).toHaveText(data.manifesto.join(''));
  await expect(page.locator('.return-map a')).toHaveCount(4);
  await expect(page.locator('.return-overview')).toContainText('不是四位作者共同提出的理论');
  await expect(page.locator('#lens-release')).toContainText('不是《奇迹课程》的逐字引文');
  await expect(page.locator('#purpose-not-status')).toContainText('不容质疑的权威');
  for(const l of data.lenses){
    const section=page.locator(`#lens-${l.id}`);
    await expect(section.locator('.citation')).toHaveCount(l.refs.length);
    await section.locator('summary').click();
    await expect(section.locator('li')).toHaveCount(3);
  }
  await expect(page.locator('.return-case')).toHaveCount(3);
  await page.locator('.return-case').first().locator('summary').click();
  await expect(page.locator('.return-case').first()).toContainText('需要处理的事实');
});

test('home and main navigation lead to the new module; late entry is not locked',async({page})=>{
  await page.goto('index.html');
  await page.locator('.return-invitation a').first().click();
  await expect(page).toHaveURL(/returning.html$/);
  await page.locator('#lens-release > a').click();
  await expect(page).toHaveURL(/returning\/explore.html#reflect-release$/);
  await expect(page.locator('[data-reflection]')).toHaveCount(4);
  await expect(page.locator('#note-release')).toBeEditable();
  await expect(page.locator('[required],[role="progressbar"]')).toHaveCount(0);
});

test('blank and partial reflections create a literal card without grading',async({page})=>{
  await page.goto('returning/explore.html');
  await page.locator('#return-preview').click();
  await expect(page.locator('#my-card')).toBeFocused();
  await expect(page.locator('#return-card-content dd')).toHaveCount(8);
  for(const dd of await page.locator('#return-card-content dd').all())await expect(dd).toHaveText('本次留白');
  const literal='<img src=x onerror=alert(1)>\n只是记录，不需要被分析。';
  await page.locator('#note-situation').fill(literal);
  await expect(page.locator('#return-card-content dd').first()).toHaveText(literal);
  await expect(page.locator('#my-card img,#my-card script')).toHaveCount(0);
  expect(await page.evaluate(key=>localStorage.getItem(key),key)).toBeNull();
});

test('switching language changes prompts without rewriting answers',async({page})=>{
  await page.goto('returning/explore.html');
  await page.locator('#note-release').fill('我仍然可以拒绝。');
  await page.locator('[name="language"][value="acim"]').check();
  await expect(page.locator('[data-release-language="acim"]')).toBeVisible();
  await expect(page.locator('[data-release-language="everyday"]')).not.toBeVisible();
  await expect(page.locator('#note-release')).toHaveValue('我仍然可以拒绝。');
  await page.locator('#return-preview').click();
  await expect(page.locator('#return-card-language')).toContainText('《奇迹课程》语言');
  await page.locator('[name="language"][value="everyday"]').check();
  await expect(page.locator('#note-release')).toHaveValue('我仍然可以拒绝。');
});

test('save and restore are explicit and a current draft is not silently overwritten',async({page})=>{
  await page.goto('returning/explore.html');
  await page.locator('#note-situation').fill('保存的版本');
  await page.locator('#return-save').click();
  await expect(page.locator('#return-status')).toContainText('没有上传');
  await page.reload();
  await expect(page.locator('#note-situation')).toHaveValue('');
  await page.locator('#return-restore').click();
  await expect(page.locator('#note-situation')).toHaveValue('保存的版本');
  await page.locator('#note-situation').fill('当前未保存');
  page.once('dialog',d=>d.dismiss());
  await page.locator('#return-restore').click();
  await expect(page.locator('#note-situation')).toHaveValue('当前未保存');
  page.once('dialog',d=>d.accept());
  await page.locator('#return-restore').click();
  await expect(page.locator('#note-situation')).toHaveValue('保存的版本');
});

test('export contains only the reader fields and does not upload',async({page})=>{
  const sent=[];
  page.on('request',r=>{if(new URL(r.url()).hostname!=='127.0.0.1'||r.method()!=='GET')sent.push(r.url());});
  await page.goto('returning/explore.html');
  await page.locator('#note-aliveness').fill('我愿意认真地听。');
  await page.locator('#note-boundary').fill('不替他作决定。');
  const wait=page.waitForEvent('download');
  await page.locator('#return-export').click();
  const dl=await wait;
  expect(dl.suggestedFilename()).toBe('ways-home-return-card.md');
  const text=fs.readFileSync(await dl.path(),'utf8');
  expect(text).toContain('我愿意认真地听。');
  expect(text).toContain('不替他作决定。');
  expect(text).toContain('本次留白');
  expect(sent).toEqual([]);
  expect(await page.evaluate(key=>localStorage.getItem(key),key)).toBeNull();
});

test('clearing requires confirmation and leaves other practices intact',async({page})=>{
  await page.goto('returning/explore.html');
  await page.evaluate(()=>localStorage.setItem('ways.home.notes.v1.look','keep me'));
  await page.locator('#note-action').fill('去散步。');
  await page.locator('#return-save').click();
  page.once('dialog',d=>d.dismiss());
  await page.locator('#return-clear').click();
  await expect(page.locator('#note-action')).toHaveValue('去散步。');
  page.once('dialog',d=>d.accept());
  await page.locator('#return-clear').click();
  await expect(page.locator('#note-action')).toHaveValue('');
  expect(await page.evaluate(key=>localStorage.getItem(key),key)).toBeNull();
  expect(await page.evaluate(()=>localStorage.getItem('ways.home.notes.v1.look'))).toBe('keep me');
});

test('storage failures and malformed records do not masquerade as success',async({page})=>{
  await page.goto('returning/explore.html');
  await page.evaluate(key=>localStorage.setItem(key,JSON.stringify({version:1,language:'acim',fields:{}})),key);
  await page.locator('#note-situation').fill('保留原文');
  await page.locator('#return-restore').click();
  await expect(page.locator('#return-status')).toContainText('格式不兼容');
  await expect(page.locator('#note-situation')).toHaveValue('保留原文');
  await page.evaluate(()=>{Storage.prototype.setItem=()=>{throw new Error('blocked');};});
  await page.locator('#return-save').click();
  await expect(page.locator('#return-status')).toContainText('保存未成功');
  await expect(page.locator('#note-situation')).toHaveValue('保留原文');
});

test('leaving an unsaved reflection requires a browser confirmation',async({page})=>{
  await page.goto('returning/explore.html');
  await page.locator('#note-situation').fill('尚未保存');
  const dialog=page.waitForEvent('dialog');
  const leaving=page.reload({timeout:2000}).catch(()=>null);
  const d=await dialog;
  expect(d.type()).toBe('beforeunload');
  await d.dismiss();
  await leaving;
  await expect(page.locator('#note-situation')).toHaveValue('尚未保存');
});

test('return pages work without scripts and new pages are searchable',async({browser,page})=>{
  const context=await browser.newContext({javaScriptEnabled:false});
  const p=await context.newPage();
  await p.goto('http://127.0.0.1:8785/ways.home/returning/explore.html');
  await expect(p.locator('[data-reflection]')).toHaveCount(4);
  await expect(p.locator('#note-situation')).toBeEditable();
  await expect(p.locator('#return-save')).not.toBeVisible();
  await expect(p.locator('.no-js-note')).toBeVisible();
  await context.close();
  await page.goto('index.html');
  await page.getByRole('button',{name:'搜索全站'}).click();
  await page.locator('#site-search').fill('探索手记');
  await expect(page.locator('.search-result').first()).toContainText('探索手记');
});

test('visual review of the module and workbook at desktop and mobile widths',async({page})=>{
  for(const width of [390,900,1440]){
    await page.setViewportSize({width,height:960});
    await page.goto('returning.html');
    expect(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth)).toBeLessThanOrEqual(1);
    await page.screenshot({path:`preview-returning-${width}.png`});
    await page.locator('.return-map').scrollIntoViewIfNeeded();
    await page.screenshot({path:`preview-returning-map-${width}.png`});
    await page.goto('returning/explore.html');
    await page.locator('#reflect-release').scrollIntoViewIfNeeded();
    await page.screenshot({path:`preview-returning-notes-${width}.png`});
  }
});
