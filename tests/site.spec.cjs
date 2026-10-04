const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const pages = JSON.parse(fs.readFileSync('assets/page-manifest.json', 'utf8'));

for (const width of [320, 390, 768, 1440]) {
  test(`all pages render without overflow at ${width}px`, async ({ page }) => {
    await page.setViewportSize({ width, height: 920 });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    for (const file of pages) {
      const response = await page.goto(file);
      expect(response.status(), file).toBe(200);
      await expect(page.locator('main h1'), file).toBeVisible();
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth);
      expect(overflow, `${file} horizontal overflow`).toBeLessThanOrEqual(1);
      await expect(page.locator('footer blockquote')).toContainText('天下同归而殊涂');
    }
    expect(errors).toEqual([]);
  });
}

test('home has four real gateways and all nine path links', async ({ page }) => {
  await page.goto('index.html');
  await expect(page.locator('.gateway')).toHaveCount(4);
  await expect(page.locator('.index-row')).toHaveCount(9);
  await page.locator('.gateway').first().click();
  await expect(page).toHaveURL(/questions\/truth\.html/);
  await expect(page.locator('.article-section')).toHaveCount(4);
  await page.screenshot({ path: 'preview-article.png', fullPage: true });
});

test('atlas filters combine, reset, and survive reload', async ({ page }) => {
  await page.goto('atlas.html');
  await expect(page.locator('[data-road]:visible')).toHaveCount(9);
  await page.getByRole('button', { name: '近美', exact: true }).click();
  await expect(page.locator('[data-road]:visible')).toHaveCount(3);
  await page.locator('#atlas-query').fill('艺术');
  await expect(page.locator('[data-road]:visible')).toHaveCount(1);
  await page.reload();
  await expect(page.locator('[data-road]:visible')).toHaveCount(1);
  await expect(page.locator('#atlas-query')).toHaveValue('艺术');
  await page.locator('#atlas-query').fill('zzzz-no-result');
  await expect(page.locator('#atlas-empty')).toBeVisible();
  await expect(page.locator('[data-road]:visible')).toHaveCount(0);
  await page.locator('#atlas-reset').click();
  await expect(page.locator('[data-road]:visible')).toHaveCount(9);
  await page.screenshot({ path: 'preview-atlas.png', fullPage: true });
});

test('global search works from a nested page and closes with focus restored', async ({ page }) => {
  await page.goto('paths/art.html');
  await page.getByRole('button', { name: '搜索全站' }).click();
  await expect(page.locator('#site-search')).toBeFocused();
  await page.locator('#site-search').fill('无我');
  await expect(page.locator('.search-result').first()).toBeVisible();
  await expect(page.locator('#search-status')).toContainText('找到');
  await page.keyboard.press('Escape');
  await expect(page.locator('#search-dialog')).not.toBeVisible();
  await expect(page.getByRole('button', { name: '搜索全站' })).toBeFocused();
  await page.keyboard.press('Control+k');
  await page.locator('#site-search').fill('zxy-no-result');
  await expect(page.locator('#search-status')).toContainText('暂时没有匹配');
  await page.locator('#site-search').fill('生态与系统');
  await page.locator('.search-result').first().click();
  await expect(page).toHaveURL(/\/paths\/ecology\.html/);
});

test('search failure is explicit and retry works', async ({ page }) => {
  await page.route('**/search-index.json', route => route.abort());
  await page.goto('index.html');
  await page.getByRole('button', { name: '搜索全站' }).click();
  await expect(page.locator('#search-status')).toContainText('暂时没有载入');
  await page.keyboard.press('Escape');
  await page.unroute('**/search-index.json');
  await page.getByRole('button', { name: '搜索全站' }).click();
  await page.locator('#site-search').fill('艺术');
  await expect(page.locator('.search-result').first()).toBeVisible();
});

test('comparison preserves distinctions, swaps, and is shareable', async ({ page }) => {
  await page.goto('unity.html');
  await expect(page.locator('#compare-a h3')).toHaveText('无我与解脱');
  await expect(page.locator('#compare-b h3')).toHaveText('梵我不二');
  await page.locator('#compare-left').selectOption('scientific');
  await expect(page.locator('#compare-a h3')).toHaveText('理论的统一');
  await page.locator('#compare-swap').click();
  await expect(page.locator('#compare-b h3')).toHaveText('理论的统一');
  await page.reload();
  await expect(page.locator('#compare-b h3')).toHaveText('理论的统一');
  await page.screenshot({ path: 'preview-comparison.png', fullPage: true });
  await page.goto('unity.html#buddhist');
  await expect(page.locator('details#buddhist')).toHaveAttribute('open', '');
});

test('sources and encounters filter with honest empty state', async ({ page }) => {
  await page.goto('encounters.html');
  await page.locator('#region-filter').selectOption('西非');
  await expect(page.locator('.encounter-item:visible')).toHaveCount(2);
  await page.goto('sources.html');
  await page.locator('#source-query').fill('NIMH');
  await expect(page.locator('[data-source]:visible')).toHaveCount(1);
  await page.locator('#source-query').fill('unmatched-zxy');
  await expect(page.locator('#source-empty')).toBeVisible();
});

test('practice timer pauses, resumes, finishes, and resets', async ({ page }) => {
  await page.clock.install();
  await page.goto('practice.html');
  await page.locator('[data-practice="pause"]').click();
  await expect(page.locator('#timer-face')).toHaveText('01:00');
  await page.locator('#timer-toggle').click();
  await page.clock.fastForward(15000);
  await expect(page.locator('#timer-face')).toHaveText('00:45');
  await page.locator('#timer-toggle').click();
  await page.clock.fastForward(10000);
  await expect(page.locator('#timer-face')).toHaveText('00:45');
  await page.locator('#timer-toggle').click();
  await page.clock.fastForward(46000);
  await expect(page.locator('#timer-face')).toHaveText('00:00');
  await expect(page.locator('#timer-status')).toContainText('结束了');
  await page.locator('#timer-reset').click();
  await expect(page.locator('#timer-face')).toHaveText('01:00');
  await page.keyboard.press('Escape');
  await expect(page.locator('#practice-dialog')).not.toBeVisible();
  await expect(page.locator('[data-practice="pause"]')).toBeFocused();
});

test('two-person practice switches after three minutes', async ({ page }) => {
  await page.clock.install();
  await page.goto('practice.html');
  await page.locator('[data-practice="listen"]').click();
  await page.locator('#timer-toggle').click();
  await expect(page.locator('#timer-status')).toContainText('第一位说话');
  await page.clock.fastForward(180000);
  await expect(page.locator('#timer-status')).toContainText('现在交换');
});

test('notes are opt-in, persist, export, and can be cleared', async ({ page }) => {
  await page.goto('practice.html');
  await page.locator('[data-practice="look"]').click();
  await page.locator('#practice-note').fill('只记录细节，不急着解释。');
  expect(await page.evaluate(() => localStorage.getItem('ways.home.notes.v1.look'))).toBeNull();
  await page.locator('#note-save').click();
  await expect(page.locator('#note-status')).toContainText('没有上传');
  await page.locator('#practice-close').click();
  await page.reload();
  await page.locator('[data-practice="look"]').click();
  await expect(page.locator('#practice-note')).toHaveValue('只记录细节，不急着解释。');
  const downloadEvent = page.waitForEvent('download');
  await page.locator('#note-export').click();
  const download = await downloadEvent;
  expect(download.suggestedFilename()).toBe('ways-home-look.txt');
  await page.screenshot({ path: 'preview-practice.png' });
  page.once('dialog', dialog => dialog.accept());
  await page.locator('#note-clear').click();
  await expect(page.locator('#practice-note')).toHaveValue('');
  expect(await page.evaluate(() => localStorage.getItem('ways.home.notes.v1.look'))).toBeNull();
});

test('storage failure does not masquerade as a save', async ({ page }) => {
  await page.addInitScript(() => {
    Storage.prototype.setItem = () => { throw new DOMException('Blocked', 'SecurityError'); };
  });
  await page.goto('practice.html');
  await page.locator('[data-practice="pause"]').click();
  await page.locator('#practice-note').fill('temporary');
  await page.locator('#note-save').click();
  await expect(page.locator('#note-status')).toContainText('保存未成功');
});

test('mobile navigation and dialogs fit the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('index.html');
  await expect(page.locator('#primary-nav')).not.toBeVisible();
  await page.getByRole('button', { name: '目录', exact: true }).click();
  await expect(page.locator('#primary-nav')).toBeVisible();
  await page.keyboard.press('Escape');
  await expect(page.locator('#primary-nav')).not.toBeVisible();
  await page.screenshot({ path: 'preview-mobile.png', fullPage: true });
  await page.goto('practice.html');
  await page.locator('[data-practice="pause"]').click();
  expect(await page.locator('#practice-dialog').evaluate(el => el.scrollWidth <= el.clientWidth + 1)).toBe(true);
  await page.screenshot({ path: 'preview-practice-mobile.png' });
});

test('content and links remain usable without JavaScript', async ({ browser }) => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:8785/ways.home/index.html');
  await expect(page.locator('#primary-nav')).toBeVisible();
  await page.locator('.gateway').first().click();
  await expect(page.locator('.article-section')).toHaveCount(4);
  await context.close();
});

test('desktop visual review captures', async ({ page }) => {
  await page.goto('index.html');
  await page.screenshot({ path: 'preview-desktop.png', fullPage: true });
  await page.screenshot({ path: 'preview-hero.png' });
});
