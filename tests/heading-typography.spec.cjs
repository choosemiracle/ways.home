const {test,expect}=require('@playwright/test');
const fs=require('node:fs');
const pages=JSON.parse(fs.readFileSync('assets/page-manifest.json','utf8'));

async function layout(page) {
  return page.evaluate(() => [...document.querySelectorAll('h1,h2,h3')].filter(h=>h.checkVisibility()).map(h=>{
    const lines=new Map();
    const walker=document.createTreeWalker(h,NodeFilter.SHOW_TEXT);
    let node;
    while(node=walker.nextNode()){
      for(let i=0;i<node.length;i++){
        if(!node.data[i].trim())continue;
        const range=document.createRange();range.setStart(node,i);range.setEnd(node,i+1);
        const r=range.getBoundingClientRect();if(!r.width)continue;
        const y=Math.round(r.top);
        const entry=[...lines.keys()].find(k=>Math.abs(k-y)<3)??y;
        lines.set(entry,(lines.get(entry)||'')+node.data[i]);
      }
    }
    const box=h.getBoundingClientRect();
    const broken=[];
    for(const u of h.querySelectorAll('.title-unit:not(.title-unit--fluid)')){
      const range=document.createRange();range.selectNodeContents(u);
      const rects=[...range.getClientRects()].filter(r=>r.width>0);
      if(rects.some(r=>r.right>box.right+2||r.left<box.left-2))broken.push({text:u.textContent,type:'overflow'});
      if(new Set(rects.map(r=>Math.round(r.top))).size>1)broken.push({text:u.textContent,type:'split'});
    }
    return {level:h.tagName,text:h.textContent,lines:[...lines.values()],font:parseFloat(getComputedStyle(h).fontSize),height:box.height,lineHeight:parseFloat(getComputedStyle(h).lineHeight),broken};
  }));
}

for(const width of [320,360,390,600,768,850,1024,1280,1440,1920]){
  test(`semantic heading audit for all pages at ${width}px`,async({page})=>{
    await page.setViewportSize({width,height:1000});
    const failures=[];const report=[];
    for(const path of pages){
      await page.goto(path);
      await page.evaluate(()=>document.fonts.ready);
      const headings=await layout(page);
      for(const h of headings){
        if(h.broken.length)failures.push({path,...h});
        if(h.lines.length>1 && h.lines.some(line=>/^[，。！？；：、）》」』】]/.test(line)))failures.push({path,reason:'leading punctuation',...h});
        if(h.level==='H1' && h.lines.length>4)failures.push({path,reason:'excessive h1 lines',...h});
        if(h.level==='H1' && h.height>h.lineHeight*(h.lines.length+0.2))failures.push({path,reason:'blank line between clauses',...h});
        if(h.lines.length>1 && h.lines.at(-1).replace(/[\s↗→↑，。！？；：]/g,'').length<2)failures.push({path,reason:'orphaned final character',...h});
      }
      report.push({path,headings});
      expect(await page.evaluate(()=>document.documentElement.scrollWidth-innerWidth),path).toBeLessThanOrEqual(1);
    }
    fs.mkdirSync('test-results',{recursive:true});
    fs.writeFileSync(`test-results/headings-${width}.json`,JSON.stringify(report,null,2));
    expect(failures).toEqual([]);
  });
}

test('reported titles break at their commas, not inside words',async({page})=>{
  for(const [path,expected] of [
    ['paths/ethics.html',['陌生人与意见不同的人，','怎样有尊严地生活在一起？']],
    ['paths/religion.html',['有限的生命，','怎样回应超出自己的意义与责任？']]
  ]){
    for(const width of [768,1024,1440,1920]){
      await page.setViewportSize({width,height:920});await page.goto(path);
      const title=(await layout(page)).find(h=>h.level==='H1');
      expect(title.lines).toEqual(expected);expect(title.font).toBeLessThanOrEqual(46);
    }
    await page.setViewportSize({width:1440,height:960});await page.goto(path);
    await page.screenshot({path:`preview-headings-${path.includes('ethics')?'ethics':'religion'}.png`});
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:`preview-headings-${path.includes('ethics')?'ethics':'religion'}-mobile.png`});
  }
});

test('semantic typography works without scripts and keeps anchor links',async({browser})=>{
  const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:1440,height:1000}});
  const page=await context.newPage();
  await page.goto('http://127.0.0.1:8785/ways.home/paths/religion.html');
  expect((await layout(page)).find(h=>h.level==='H1').lines).toEqual(['有限的生命，','怎样回应超出自己的意义与责任？']);
  await page.locator('.depth-bridge h2 a').click();
  await expect(page).toHaveURL(/studies\/one-and-many.html/);
  await context.close();
});

test('search and image-dialog headings use the same phrase plans',async({page})=>{
  await page.goto('paths/ethics.html');
  await page.getByRole('button',{name:'搜索全站'}).click();
  await page.locator('#site-search').fill('艺术');
  await expect(page.locator('.search-result h3.title-flow').first()).toBeVisible();
  await page.keyboard.press('Escape');
  await page.goto('media.html');
  await page.locator('#image-wave [data-lightbox]').click();
  await expect(page.locator('#image-dialog-title .title-unit')).toHaveCount(2);
  await expect(page.locator('#image-dialog-title')).toHaveText('葛饰北斋《神奈川冲浪里》');
  await page.keyboard.press('Escape');
});
