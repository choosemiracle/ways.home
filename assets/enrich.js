'use strict';

// Media and applications are progressive enhancements: reading never requires them.
(() => {
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const base = new URL(document.body.dataset.base || './', location.href);

  const imageDialog = $('#image-dialog');
  let imageTrigger = null;
  $$('[data-lightbox]').forEach(anchor => anchor.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    if (!imageDialog || document.querySelector('dialog[open]')) return;
    event.preventDefault();
    const figure = anchor.closest('figure');
    const img = $('img', anchor);
    const caption = $('figcaption', figure);
    imageTrigger = anchor;
    $('#large-image').src = img.currentSrc || img.src;
    $('#large-image').alt = img.alt;
    $('#image-dialog-title').textContent = $('.image-credit strong', figure).textContent;
    $('#large-image-caption').replaceChildren(...[...caption.childNodes].map(node => node.cloneNode(true)));
    imageDialog.showModal();
    document.body.classList.add('modal-open');
    imageDialog.scrollTop = 0;
    $('[data-image-close]').focus({preventScroll:true});
  }));
  $('[data-image-close]')?.addEventListener('click', () => imageDialog.close());
  imageDialog?.addEventListener('close', () => {
    $('#large-image').removeAttribute('src');
    imageTrigger?.focus({preventScroll:true});
  });

  // No iframe, thumbnail, remote font or preconnect exists before explicit consent.
  const controllers = new WeakMap();
  $$('[data-video-card]').forEach(card => {
    const load = $('[data-load-video]',card);
    const unload = $('[data-unload-video]',card);
    const stage = $('[data-player-stage]',card);
    const status = $('[data-video-status]',card);
    const placeholder = stage.firstElementChild.cloneNode(true);
    let timeout = null;
    let player = null;
    function stop(focus=false) {
      clearTimeout(timeout);
      player?.remove();
      player = null;
      stage.replaceChildren(placeholder.cloneNode(true));
      load.hidden = false;
      unload.hidden = true;
      status.textContent = '播放器已关闭；继续阅读不需要连接外部视频平台。';
      if (focus) load.focus({preventScroll:true});
    }
    controllers.set(card, stop);
    load.addEventListener('click', () => {
      const {provider, videoId, videoTitle} = load.dataset;
      const valid = (provider==='youtube' && /^[A-Za-z0-9_-]{11}$/.test(videoId)) || (provider==='vimeo' && /^\d+$/.test(videoId));
      if (!valid || player) { if (!valid) status.textContent='资料标识无效，请使用发布出处。'; return; }
      const url = provider==='youtube'
        ? new URL(`https://www.youtube-nocookie.com/embed/${videoId}`)
        : new URL(`https://player.vimeo.com/video/${videoId}`);
      url.searchParams.set('autoplay','0');
      if (provider==='youtube') { url.searchParams.set('rel','0'); url.searchParams.set('playsinline','1'); }
      else url.searchParams.set('dnt','1');
      player = document.createElement('iframe');
      player.title = videoTitle;
      player.referrerPolicy = 'strict-origin-when-cross-origin';
      player.allow = 'fullscreen; picture-in-picture; encrypted-media';
      player.allowFullscreen = true;
      const current = player;
      player.addEventListener('load', () => {
        if (player!==current) return;
        clearTimeout(timeout);
        status.textContent='播放器框架已返回；是否可播放以平台显示为准。无画面或报错时，可使用原平台链接，或关闭后继续读导读。';
      });
      player.addEventListener('error', () => {
        clearTimeout(timeout);
        status.textContent='播放器请求未成功。可以使用原平台链接，文字导读仍然完整。';
      });
      status.textContent='正在连接所选视频平台；请在播放器出现后自行开始播放。';
      load.hidden = true;
      unload.hidden = false;
      stage.replaceChildren(player);
      timeout=setTimeout(() => { if (player===current) status.textContent='平台响应较慢或受到限制。可以关闭播放器，改用原平台链接；不影响继续阅读。'; },15000);
      player.src=url.href;
      unload.focus({preventScroll:true});
    });
    unload.addEventListener('click', () => stop(true));
  });

  const query = $('#media-query');
  if (query) {
    const items = $$('[data-media-item]');
    let kind='all';
    const normalize = text => text.normalize('NFKC').toLowerCase();
    function filter() {
      const terms=normalize(query.value).trim().split(/\s+/).filter(Boolean);
      let count=0;
      items.forEach(item => {
        const visible=(kind==='all' || item.dataset.kind===kind) && terms.every(t=>normalize(item.dataset.search).includes(t));
        if (!visible && !item.hidden) {
          $$('[data-video-card]',item).forEach(card=>controllers.get(card)?.());
        }
        item.hidden=!visible;
        if (visible) count++;
      });
      $$('[data-media-kind]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.mediaKind===kind)));
      $('#media-count').textContent=`显示 ${count} / ${items.length} 项资料`;
      $('#media-empty').hidden=count!==0;
    }
    $$('[data-media-kind]').forEach(button=>button.addEventListener('click',()=>{kind=button.dataset.mediaKind;filter();}));
    query.addEventListener('input',filter);
    $('#media-reset').addEventListener('click',()=>{kind='all';query.value='';filter();});
    window.addEventListener('hashchange',()=>{kind='all';query.value='';filter();});
  }

  let plans = null;
  let planLoading = null;
  async function loadPlans() {
    if (plans) return plans;
    if (!planLoading) {
      planLoading=fetch(new URL('assets/workshops.json',base)).then(r=>{
        if (!r.ok) throw new Error('Plan request failed');
        return r.json();
      }).then(data=>{
        if (!Array.isArray(data) || !data.every(p=>typeof p.id==='string' && Array.isArray(p.steps) && typeof p.title==='string')) throw new Error('Invalid plans');
        plans=data;
        return data;
      }).finally(()=>{planLoading=null;});
    }
    return planLoading;
  }
  function planMarkdown(plan) {
    const lines=[`# ${plan.title}`, '', '同归 · WAYS HOME / 本站原创应用流程', '', `时长：${plan.duration} 分钟`, `适用：${plan.audience}`, '', `目标：${plan.focus}`, '', '## 准备材料', plan.material, '', `深读：${new URL('studies/'+plan.study+'.html',base).href}`, `视频导读：${new URL('media.html#video-'+plan.video,base).href}`, '', '## 流程'];
    let elapsed=0;
    plan.steps.forEach(step=>{lines.push('',`### ${elapsed}—${elapsed+step.minutes} 分钟 / ${step.title}`,step.text);elapsed+=step.minutes;});
    lines.push('','## 开放问题',...plan.questions.map(q=>'- '+q),'','## 具体产出',plan.output,'','## 适用边界',plan.boundary,'','## 怎样复盘',plan.review,'','## 自己的记录','','','本流程不承诺特定心理或学习效果，也不替代组织授权、专业评估或完整宗教修法。');
    return lines.join('\n');
  }
  $$('[data-export-plan]').forEach(button=>button.addEventListener('click',async()=>{
    const status=$('[data-plan-status]',button.closest('[data-workshop]'));
    button.disabled=true;
    status.textContent='正在准备完整流程…';
    try {
      const list=await loadPlans();
      const plan=list.find(p=>p.id===button.dataset.exportPlan);
      if (!plan) throw new Error('Missing plan');
      const blob=new Blob([planMarkdown(plan)],{type:'text/markdown;charset=utf-8'});
      const url=URL.createObjectURL(blob);
      const a=document.createElement('a');
      a.href=url;a.download=`ways-home-${plan.id}.md`;
      document.body.append(a);a.click();a.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      status.textContent='已生成流程文件；请确认浏览器保存成功。';
    } catch { status.textContent='导出未成功。可以重试，或直接使用页面中的完整流程。'; }
    finally {button.disabled=false;}
  }));

  function clearPrint() {
    document.body.classList.remove('print-one');
    $$('.print-active').forEach(item=>item.classList.remove('print-active'));
  }
  $$('[data-print-plan]').forEach(button=>button.addEventListener('click',()=>{
    clearPrint();
    button.closest('[data-workshop]').classList.add('print-active');
    document.body.classList.add('print-one');
    window.print();
  }));
  window.addEventListener('afterprint',clearPrint);
})();
