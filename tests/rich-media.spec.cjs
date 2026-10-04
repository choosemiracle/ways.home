const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const workshops = JSON.parse(fs.readFileSync('content/workshops.json','utf8'));
const depth = JSON.parse(fs.readFileSync('content/depth.json','utf8'));
const media = JSON.parse(fs.readFileSync('content/media.json','utf8'));

test('six deep studies have substantive sections, objections and guided media', async ({ page }) => {
  await page.goto('studies.html');
  await expect(page.locator('.study-card')).toHaveCount(6);
  await expect(page.locator('.glossary-grid article')).toHaveCount(12);
  for (const study of depth.studies) {
    await page.goto(`studies/${study.id}.html`);
    await expect(page.locator('.article-section')).toHaveCount(6);
    await expect(page.locator('.objection-box')).toBeVisible();
    await expect(page.locator('.follow-questions li')).toHaveCount(3);
    await expect(page.locator('[data-video-card]')).toHaveCount(1);
    expect((await page.locator('.reading-column').innerText()).length).toBeGreaterThan(1700);
  }
});

test('images load at full proportions, have credit and can be enlarged', async ({ page }) => {
  await page.goto('media.html');
  await expect(page.locator('[data-kind="image"]')).toHaveCount(5);
  for (const figure of await page.locator('.archive-figure').all()) {
    await figure.scrollIntoViewIfNeeded();
    const image = figure.locator('img');
    await expect.poll(() => image.evaluate(i=>i.complete && i.naturalWidth>100)).toBe(true);
    expect(await image.getAttribute('alt')).toBeTruthy();
    await expect(figure.locator('.image-credit')).toContainText(/Public Domain|公共领域/);
    expect(await image.evaluate(i=>getComputedStyle(i).objectFit)).toBe('contain');
  }
  const trigger=page.locator('[data-lightbox]').first();
  await trigger.click();
  await expect(page.locator('#image-dialog')).toBeVisible();
  await expect(page.locator('#large-image-caption')).toContainText('NASA');
  await expect(page.locator('[data-image-close]')).toBeFocused();
  await page.keyboard.press('Escape');
  await expect(page.locator('#image-dialog')).not.toBeVisible();
  await expect(trigger).toBeFocused();
});

test('no third-party network requests occur before video consent', async ({ page }) => {
  const requests=[];
  page.on('request',r=>{if(new URL(r.url()).hostname!=='127.0.0.1') requests.push(r.url());});
  await page.goto('media.html');
  await page.locator('#video-harvest').scrollIntoViewIfNeeded();
  await expect(page.locator('iframe')).toHaveCount(0);
  await expect(page.locator('[data-load-video]:visible')).toHaveCount(6);
  await expect(page.locator('[data-unload-video]:visible')).toHaveCount(0);
  expect(requests).toEqual([]);
});

for (const provider of ['youtube','vimeo']) {
  test(`${provider} embeds are consent-gated, non-autoplay, and removable`, async ({ page }) => {
    await page.route('https://www.youtube-nocookie.com/**',r=>r.fulfill({contentType:'text/html',body:'<p>Player contract test; not actual playback.</p>'}));
    await page.route('https://player.vimeo.com/**',r=>r.fulfill({contentType:'text/html',body:'<p>Player contract test; not actual playback.</p>'}));
    await page.goto('media.html');
    const load=page.locator(`[data-load-video][data-provider="${provider}"]`).first();
    const card=load.locator('xpath=ancestor::article[1]');
    await load.click();
    await expect(card.locator('iframe')).toHaveCount(1);
    const url=new URL(await card.locator('iframe').getAttribute('src'));
    expect(url.hostname).toBe(provider==='youtube'?'www.youtube-nocookie.com':'player.vimeo.com');
    expect(url.searchParams.get('autoplay')).toBe('0');
    await expect(card.locator('[data-unload-video]')).toBeVisible();
    await expect(load).not.toBeVisible();
    await expect(card.locator('[data-video-status]')).toContainText('以平台显示为准');
    await expect(card.getByRole('link',{name:'原平台观看'})).toBeVisible();
    await card.locator('[data-unload-video]').click();
    await expect(card.locator('iframe')).toHaveCount(0);
    await expect(load).toBeFocused();
  });
}

test('media search combines with type filtering and exposes empty state', async ({ page }) => {
  await page.goto('media.html');
  await page.locator('[data-media-kind="image"]').click();
  await expect(page.locator('[data-media-item]:visible')).toHaveCount(5);
  await page.locator('#media-query').fill('北斋');
  await expect(page.locator('[data-media-item]:visible')).toHaveCount(1);
  await page.locator('[data-media-kind="video"]').click();
  await expect(page.locator('[data-media-item]:visible')).toHaveCount(1);
  await page.locator('#media-query').fill('no-such-video-xyz');
  await expect(page.locator('#media-empty')).toBeVisible();
  await page.locator('#media-reset').click();
  await expect(page.locator('[data-media-item]:visible')).toHaveCount(11);
});

test('filtering away a video unloads the player rather than hiding playback', async ({ page }) => {
  await page.route('https://player.vimeo.com/**',r=>r.fulfill({contentType:'text/html',body:'<p>mock player</p>'}));
  await page.goto('media.html');
  await page.locator('[data-load-video]').first().click();
  await expect(page.locator('iframe')).toHaveCount(1);
  await page.locator('[data-media-kind="image"]').click();
  await expect(page.locator('iframe')).toHaveCount(0);
});

test('applications export full usable plans with accurate timing', async ({ page }) => {
  await page.goto('applications.html');
  await expect(page.locator('[data-workshop]')).toHaveCount(4);
  for (const plan of workshops) {
    expect(plan.steps.reduce((sum,s)=>sum+s.minutes,0)).toBe(plan.duration);
    const event=page.waitForEvent('download');
    await page.locator(`[data-export-plan="${plan.id}"]`).click();
    const download=await event;
    expect(download.suggestedFilename()).toBe(`ways-home-${plan.id}.md`);
    const content=fs.readFileSync(await download.path(),'utf8');
    expect(content).toContain(plan.title);
    expect(content).toContain(plan.boundary);
    expect(content).toContain(plan.review);
    expect(content).toContain(`studies/${plan.study}.html`);
    for (const step of plan.steps) expect(content).toContain(step.text);
  }
});

test('plan request failure is explicit, leaves page usable and supports retry', async ({ page }) => {
  await page.route('**/workshops.json',r=>r.abort());
  await page.goto('applications.html');
  const plan=page.locator('[data-workshop]').first();
  await plan.locator('[data-export-plan]').click();
  await expect(plan.locator('[data-plan-status]')).toContainText('导出未成功');
  await expect(plan.locator('.workshop-timeline')).toBeVisible();
  await page.unroute('**/workshops.json');
  const download=page.waitForEvent('download');
  await plan.locator('[data-export-plan]').click();
  await download;
});

test('selected plan print mode hides other plans, then cleans up', async ({ page }) => {
  await page.goto('applications.html');
  await page.evaluate(()=>{window.print=()=>{};});
  await page.locator('#stewardship [data-print-plan]').click();
  await page.emulateMedia({media:'print'});
  await expect(page.locator('#stewardship')).toBeVisible();
  await expect(page.locator('#looking')).not.toBeVisible();
  await page.evaluate(()=>dispatchEvent(new Event('afterprint')));
  await page.emulateMedia({media:'screen'});
  await expect(page.locator('#looking')).toBeVisible();
});

test('expanded encounters and comparisons keep old entries and add new perspectives', async ({ page }) => {
  await page.goto('encounters.html');
  await expect(page.locator('.encounter-item')).toHaveCount(15);
  await page.goto('unity.html');
  await expect(page.locator('#compare-left option')).toHaveCount(14);
  await page.locator('#compare-left').selectOption('commons');
  await expect(page.locator('#compare-a')).toContainText('多中心');
  await page.locator('#compare-right').selectOption('monist');
  await expect(page.locator('#compare-b')).toContainText('何种意义');
  await page.goto('sources.html');
  await expect(page.locator('[data-source]')).toHaveCount(37);
});

test('media and applications remain readable without JavaScript', async ({ browser }) => {
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:8785/ways.home/media.html');
  await expect(page.locator('[data-video-card]')).toHaveCount(6);
  await expect(page.locator('iframe')).toHaveCount(0);
  await expect(page.locator('[data-load-video]').first()).not.toBeVisible();
  await expect(page.getByRole('link',{name:'原平台观看'}).first()).toBeVisible();
  await page.goto('http://127.0.0.1:8785/ways.home/applications.html');
  await expect(page.locator('.workshop-timeline')).toHaveCount(4);
  await context.close();
});

test('new page and image viewer visual review at desktop and mobile widths', async ({ page }) => {
  await page.goto('studies/seeing-art.html');
  await page.locator('.archive-figure').first().scrollIntoViewIfNeeded();
  await page.screenshot({path:'preview-v4-study.png'});
  await page.goto('studies.html');
  await page.screenshot({path:'preview-v4-deep-index.png',fullPage:true});
  await page.goto('media.html#video-chalmers');
  await page.screenshot({path:'preview-v4-video.png'});
  await page.goto('applications.html#looking');
  await page.screenshot({path:'preview-v4-application.png'});
  await page.setViewportSize({width:390,height:844});
  await page.goto('studies/one-and-many.html#part-1');
  await page.screenshot({path:'preview-v4-study-mobile.png'});
  await page.goto('media.html#image-wave');
  await page.locator('#image-wave [data-lightbox]').click();
  await expect.poll(()=>page.locator('#large-image').evaluate(img=>img.complete&&img.naturalWidth>0)).toBe(true);
  expect(await page.locator('#image-dialog').evaluate(el=>el.scrollWidth-el.clientWidth)).toBeLessThanOrEqual(1);
  await page.screenshot({path:'preview-v4-lightbox-mobile.png'});
});
