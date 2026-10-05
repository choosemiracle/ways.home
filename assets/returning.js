/* A private, unscored worksheet. No API calls, no automatic storage. */
(() => {
  'use strict';
  const form = document.getElementById('return-form');
  if (!form) return;
  const fields = [...form.querySelectorAll('[data-return-field]')];
  const status = document.getElementById('return-status');
  const result = document.getElementById('my-card');
  const content = document.getElementById('return-card-content');
  const storageKey = 'ways.home.returning.v1';
  // An explicit link can select the prompt language, never load private notes.
  const requestedLanguage = new URLSearchParams(location.search).get('language');
  if (requestedLanguage === 'acim' || requestedLanguage === 'everyday') {
    form.querySelector(`[name="language"][value="${requestedLanguage}"]`).checked = true;
  }
  const languageName = value => value === 'acim' ? '《奇迹课程》语言' : '日常语言';
  const language = () => form.querySelector('[name="language"]:checked').value;
  const snapshot = () => ({ version: 1, language: language(), fields: Object.fromEntries(fields.map(f => [f.name, f.value])) });
  const signature = () => JSON.stringify(snapshot());
  let safeSignature = signature();
  const say = text => { status.textContent = text; };
  const isDirty = () => signature() !== safeSignature;

  function setLanguage() {
    const selected = language();
    form.querySelectorAll('[data-release-language]').forEach(el => {
      el.hidden = el.dataset.releaseLanguage !== selected;
      if (el.tagName === 'DETAILS') el.open = selected === 'acim';
    });
  }
  function showCard(focus = true) {
    content.replaceChildren();
    fields.forEach(field => {
      const row = document.createElement('div');
      const term = document.createElement('dt');
      term.textContent = field.dataset.label;
      const definition = document.createElement('dd');
      definition.textContent = field.value.trim() ? field.value : '本次留白';
      row.append(term, definition);
      content.append(row);
    });
    document.getElementById('return-card-language').textContent = `第四问使用：${languageName(language())}。这只是提问方式，不是身份或信仰判断。`;
    result.hidden = false;
    if (focus) {
      result.focus({ preventScroll: true });
      result.scrollIntoView({ block: 'start', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth' });
    }
  }
  function validRecord(value) {
    return value && value.version === 1 && ['everyday','acim'].includes(value.language)
      && value.fields && typeof value.fields === 'object' && !Array.isArray(value.fields)
      && Object.keys(value.fields).length === fields.length
      && fields.every(f => typeof value.fields[f.name] === 'string' && value.fields[f.name].length <= 12000);
  }
  function markdown() {
    return '# 我的回归卡\n\n这是一份自我记录，不是评测或建议。\n\n'
      + `第四问使用：${languageName(language())}。\n\n`
      + fields.map(f => `## ${f.dataset.label}\n\n${f.value.trim() ? f.value : '本次留白'}\n`).join('\n')
      + '\n本次留白不代表没有进展。这张卡只记录此刻，不定义我是谁。\n';
  }
  form.addEventListener('submit', event => event.preventDefault());
  form.addEventListener('input', () => {
    say(isDirty() ? '当前修改尚未保存；离开前可以保存或导出。' : '文字与上次保留的版本一致。');
    if (!result.hidden) showCard(false);
  });
  form.querySelectorAll('[name="language"]').forEach(radio => radio.addEventListener('change', () => {
    setLanguage();
    if (!result.hidden) showCard(false);
    say('只更换了提问语言，已写内容保持不变。修改尚未保存。');
  }));
  document.getElementById('return-preview').addEventListener('click', () => showCard());
  document.querySelectorAll('a[href="#my-card"]').forEach(a => a.addEventListener('click', event => {
    event.preventDefault();
    showCard();
  }));
  document.getElementById('return-save').addEventListener('click', () => {
    try {
      localStorage.setItem(storageKey, signature());
      safeSignature = signature();
      say('已保存在此浏览器，没有上传。再次访问时需主动点击“读取本机记录”。');
    } catch { say('保存未成功。浏览器存储可能被禁用或已满；请导出或复制文字。'); }
  });
  document.getElementById('return-restore').addEventListener('click', () => {
    let record;
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw === null) { say('此浏览器还没有本模块的记录。当前文字未改动。'); return; }
      record = JSON.parse(raw);
      if (!validRecord(record)) { say('本机记录格式不兼容或已损坏，未覆盖当前文字。'); return; }
    } catch { say('读取未成功，当前文字未改动。请检查浏览器存储设置。'); return; }
    if (isDirty() && !confirm('读取会替换当前未保存的手记。确定继续吗？')) return;
    fields.forEach(f => { f.value = record.fields[f.name]; });
    form.querySelector(`[name="language"][value="${record.language}"]`).checked = true;
    setLanguage();
    safeSignature = signature();
    if (!result.hidden) showCard(false);
    say('已读取此浏览器的手记；没有联网或生成分析。');
  });
  document.getElementById('return-export').addEventListener('click', () => {
    let url;
    try {
      url = URL.createObjectURL(new Blob([markdown()], { type:'text/markdown;charset=utf-8' }));
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'ways-home-return-card.md';
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      say('已生成回归卡文件。请确认文件保存成功；未更改本浏览器记录。');
    } catch { say('导出未成功。请整理回归卡后，直接复制其中的文字。'); }
    finally { if (url) setTimeout(() => URL.revokeObjectURL(url), 1000); }
  });
  document.getElementById('return-clear').addEventListener('click', () => {
    if (!confirm('清除当前手记及此浏览器的回归之路记录？其他练习的记录不会删除。')) return;
    try { localStorage.removeItem(storageKey); }
    catch { say('未能确认删除本机记录。当前文字未改动，请在浏览器设置中处理网站存储。'); return; }
    fields.forEach(f => { f.value = ''; });
    form.querySelector('[name="language"][value="everyday"]').checked = true;
    setLanguage();
    safeSignature = signature();
    content.replaceChildren();
    result.hidden = true;
    say('本模块的本机记录与当前草稿已清除，其他练习不受影响。');
  });
  addEventListener('beforeunload', event => {
    if (isDirty()) { event.preventDefault(); event.returnValue = ''; }
  });
  // Do not read or reveal saved content on page load, especially on shared devices.
  setLanguage();
})();
