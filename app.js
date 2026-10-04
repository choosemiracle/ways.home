'use strict';

/* Progressive enhancements only: all reading content exists in the HTML. */
(() => {
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const base = new URL(document.body.dataset.base || './', location.href);
  const normalize = value => String(value).normalize('NFKC').toLocaleLowerCase().trim();
  const terms = value => normalize(value).split(/\s+/).filter(Boolean);
  const matches = (text, query) => terms(query).every(term => normalize(text).includes(term));
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const scrollTo = element => element?.scrollIntoView({ behavior: reducedMotion.matches ? 'instant' : 'smooth', block: 'start' });

  function updateParams(changes) {
    const url = new URL(location.href);
    Object.entries(changes).forEach(([key, value]) => {
      if (value === '' || value === null || value === 'all') url.searchParams.delete(key);
      else url.searchParams.set(key, value);
    });
    history.replaceState(null, '', url);
  }

  // Responsive navigation remains visible if JavaScript is disabled.
  const menu = $('.menu-button');
  const nav = $('#primary-nav');
  function closeMenu() {
    nav?.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
  }
  menu?.addEventListener('click', () => {
    const open = !nav.classList.contains('open');
    nav.classList.toggle('open', open);
    menu.setAttribute('aria-expanded', String(open));
  });
  nav?.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('click', event => { if (!event.target.closest('.site-header')) closeMenu(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && nav?.classList.contains('open')) { closeMenu(); menu.focus(); }
  });
  window.matchMedia('(max-width: 850px)').addEventListener('change', closeMenu);

  // A quiet reading-progress line; not an achievement score.
  const progress = $('.reading-progress span');
  let framePending = false;
  function updateProgress() {
    const extent = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.transform = `scaleX(${extent > 0 ? Math.min(1, Math.max(0, scrollY / extent)) : 0})`;
    framePending = false;
  }
  window.addEventListener('scroll', () => {
    if (!framePending) { framePending = true; requestAnimationFrame(updateProgress); }
  }, { passive: true });
  window.addEventListener('resize', updateProgress);
  updateProgress();

  // Native modal dialogs supply keyboard trapping and Escape behavior.
  const dialogFocus = new WeakMap();
  function openDialog(dialog, focusTarget) {
    if (document.querySelector('dialog[open]')) return;
    dialogFocus.set(dialog, document.activeElement);
    dialog.showModal();
    document.body.classList.add('modal-open');
    dialog.scrollTop = 0;
    focusTarget?.focus({ preventScroll: true });
  }
  $$('dialog').forEach(dialog => {
    // Search inputs may consume Escape to clear text before native dialog handling.
    dialog.addEventListener('keydown', event => {
      if (event.key === 'Escape' && !event.isComposing) {
        event.preventDefault();
        event.stopPropagation();
        dialog.close();
      }
    }, true);
    dialog.addEventListener('close', () => {
      document.body.classList.toggle('modal-open', !!document.querySelector('dialog[open]'));
      dialogFocus.get(dialog)?.focus({ preventScroll: true });
    });
  });

  // Site-local full-text search. No query leaves this site.
  const searchDialog = $('#search-dialog');
  const searchInput = $('#site-search');
  const searchStatus = $('#search-status');
  const searchResults = $('#search-results');
  let index = null;
  let indexLoading = null;

  function renderSearch() {
    searchResults.replaceChildren();
    const query = terms(searchInput.value);
    if (!query.length) {
      searchStatus.textContent = '输入一个词，查找本站文章、历史切面与来源。';
      return;
    }
    if (!index) return;
    const found = index.map(item => {
      const haystack = normalize(`${item.title} ${item.description} ${item.text}`);
      const score = query.every(term => haystack.includes(term))
        ? query.reduce((sum, term) => sum + (normalize(item.title).includes(term) ? 10 : 0) + (normalize(item.description).includes(term) ? 3 : 1), 0)
        : 0;
      return { item, score };
    }).filter(result => result.score > 0).sort((a, b) => b.score - a.score);
    searchStatus.textContent = found.length ? `找到 ${found.length} 个页面${found.length > 8 ? '，先显示最相关的 8 个' : ''}。` : '暂时没有匹配。试试更简短的词，例如“艺术”或“关系”。';
    found.slice(0, 8).forEach(({ item }) => {
      const anchor = document.createElement('a');
      anchor.className = 'search-result';
      anchor.href = new URL(item.url, base).href;
      const kind = document.createElement('small');
      kind.textContent = item.kind;
      const title = document.createElement('h3');
      title.textContent = item.title;
      const excerpt = document.createElement('p');
      const offset = Math.max(0, normalize(item.text).indexOf(query[0]) - 28);
      excerpt.textContent = `${offset ? '…' : ''}${item.text.slice(offset, offset + 125)}${item.text.length > offset + 125 ? '…' : ''}`;
      anchor.append(kind, title, excerpt);
      searchResults.append(anchor);
    });
  }

  async function loadSearch() {
    if (index) { renderSearch(); return; }
    searchStatus.textContent = '正在打开本站索引…';
    if (!indexLoading) {
      indexLoading = fetch(new URL('assets/search-index.json', base))
        .then(response => {
          if (!response.ok) throw new Error(`Search index HTTP ${response.status}`);
          return response.json();
        })
        .then(data => {
          if (!Array.isArray(data) || !data.every(item => typeof item.title === 'string' && typeof item.text === 'string' && typeof item.description === 'string' && /^(?:[a-z]+\/)?[a-z0-9-]+\.html$/.test(item.url))) {
            throw new Error('Invalid search index');
          }
          index = data;
        })
        .finally(() => { indexLoading = null; });
    }
    try { await indexLoading; renderSearch(); }
    catch { searchStatus.textContent = '索引暂时没有载入。可以关闭后重试，或直接从“探索图谱”阅读。'; }
  }
  function showSearch() {
    if (document.querySelector('dialog[open]')) return;
    closeMenu();
    openDialog(searchDialog, searchInput);
    loadSearch();
  }
  $$('[data-search-open]').forEach(button => button.addEventListener('click', showSearch));
  $('[data-search-close]')?.addEventListener('click', () => searchDialog.close());
  searchInput?.addEventListener('input', renderSearch);
  searchInput?.addEventListener('keydown', event => {
    if (event.key === 'ArrowDown') { const first = $('a', searchResults); if (first) { event.preventDefault(); first.focus(); } }
  });
  document.addEventListener('keydown', event => {
    if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); showSearch(); }
  });

  // Atlas URL state can be bookmarked and shared.
  const atlasQuery = $('#atlas-query');
  if (atlasQuery) {
    const cards = $$('[data-road]');
    const buttons = $$('[data-lens]');
    const allowed = buttons.map(button => button.dataset.lens);
    let lens = 'all';
    function filterAtlas(writeURL = true) {
      const query = atlasQuery.value.trim();
      let count = 0;
      cards.forEach(card => {
        const show = (lens === 'all' || card.dataset.tags.split(' ').includes(lens)) && matches(card.dataset.search, query);
        card.hidden = !show;
        if (show) count += 1;
      });
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lens === lens)));
      $('#atlas-count').textContent = `显示 ${count} / ${cards.length} 条探索路径`;
      $('#atlas-empty').hidden = count !== 0;
      if (writeURL) updateParams({ lens, q: query });
      updateProgress();
    }
    function restoreAtlas() {
      const params = new URLSearchParams(location.search);
      lens = allowed.includes(params.get('lens')) ? params.get('lens') : 'all';
      atlasQuery.value = (params.get('q') || '').slice(0, 160);
      filterAtlas(false);
    }
    buttons.forEach(button => button.addEventListener('click', () => { lens = button.dataset.lens; filterAtlas(); }));
    atlasQuery.addEventListener('input', () => filterAtlas());
    $('#atlas-reset').addEventListener('click', () => { lens = 'all'; atlasQuery.value = ''; filterAtlas(); });
    window.addEventListener('popstate', restoreAtlas);
    restoreAtlas();
  }

  const regionFilter = $('#region-filter');
  if (regionFilter) {
    const items = $$('.encounter-item');
    function filterRegion() {
      let count = 0;
      items.forEach(item => {
        item.hidden = regionFilter.value !== 'all' && regionFilter.value !== item.dataset.region;
        if (!item.hidden) count += 1;
      });
      $('#encounter-count').textContent = `${count} / ${items.length} 个切面`;
      updateProgress();
    }
    regionFilter.addEventListener('change', filterRegion);
    window.addEventListener('hashchange', () => { regionFilter.value = 'all'; filterRegion(); });
  }

  const sourceQuery = $('#source-query');
  if (sourceQuery) {
    const entries = $$('[data-source]');
    function filterSources() {
      let count = 0;
      entries.forEach(entry => { entry.hidden = !matches(entry.dataset.search, sourceQuery.value); if (!entry.hidden) count += 1; });
      $('#source-count').textContent = `${count} / ${entries.length} 项来源`;
      $('#source-empty').hidden = count !== 0;
      updateProgress();
    }
    sourceQuery.addEventListener('input', filterSources);
    window.addEventListener('hashchange', () => { sourceQuery.value = ''; filterSources(); });
  }

  // Comparison uses trusted, pre-rendered templates. No user HTML is inserted.
  const left = $('#compare-left');
  const right = $('#compare-right');
  if (left && right) {
    const templates = new Map($$('template[data-tradition]').map(template => [template.dataset.tradition, template]));
    function renderComparison(writeURL = true) {
      $('#compare-a').replaceChildren(templates.get(left.value).content.cloneNode(true));
      $('#compare-b').replaceChildren(templates.get(right.value).content.cloneNode(true));
      $('#compare-status').textContent = left.value === right.value
        ? '当前两侧相同；可以选择另一个入口，看看区别在哪里。'
        : `${left.selectedOptions[0].textContent} × ${right.selectedOptions[0].textContent}`;
      if (writeURL) updateParams({ left: left.value, right: right.value });
    }
    function restoreComparison() {
      const params = new URLSearchParams(location.search);
      left.value = templates.has(params.get('left')) ? params.get('left') : 'buddhist';
      right.value = templates.has(params.get('right')) ? params.get('right') : 'advaita';
      renderComparison(false);
    }
    left.addEventListener('change', () => renderComparison());
    right.addEventListener('change', () => renderComparison());
    $('#compare-swap').addEventListener('click', () => { [left.value, right.value] = [right.value, left.value]; renderComparison(); });
    window.addEventListener('popstate', restoreComparison);
    restoreComparison();
  }

  function revealHash() {
    if (!location.hash) return;
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
    const target = document.getElementById(id);
    if (target?.tagName === 'DETAILS') { target.open = true; scrollTo(target); }
  }
  revealHash();
  window.addEventListener('hashchange', revealHash);

  // Voluntary practice timer: wall-clock deadline avoids background-tab drift.
  const practiceDialog = $('#practice-dialog');
  if (practiceDialog) {
    const face = $('#timer-face');
    const timerStatus = $('#timer-status');
    const toggle = $('#timer-toggle');
    const note = $('#practice-note');
    const noteStatus = $('#note-status');
    const drafts = new Map();
    const storagePrefix = 'ways.home.notes.v1.';
    let state = { id: '', title: '', total: 0, remaining: 0, deadline: 0, mode: 'ready' };
    let interval = null;
    let savedValue = '';
    const format = ms => {
      const seconds = Math.ceil(Math.max(0, ms) / 1000);
      return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
    };
    function setStatus(text) { if (timerStatus.textContent !== text) timerStatus.textContent = text; }
    function stageText() {
      if (state.id !== 'listen') return '正在进行。随时可以暂停或结束。';
      return state.remaining > state.total / 2 ? '第一位说话，第二位聆听。' : '现在交换：第二位说话，第一位聆听。';
    }
    function tick() {
      if (state.mode !== 'running') return;
      state.remaining = Math.max(0, state.deadline - Date.now());
      face.textContent = format(state.remaining);
      if (state.remaining === 0) {
        state.mode = 'finished';
        clearInterval(interval);
        interval = null;
        toggle.textContent = '再开始一次';
        setStatus('这段时间结束了。没有结论，也可以。');
      } else setStatus(stageText());
    }
    function resetTimer() {
      clearInterval(interval);
      interval = null;
      state.mode = 'ready';
      state.remaining = state.total;
      face.textContent = format(state.remaining);
      toggle.textContent = '开始';
      setStatus(`准备时间 ${format(state.total)}，准备好了再开始。`);
    }
    function stashDraft() {
      if (state.id) drafts.set(state.id, { text: note.value, saved: savedValue });
    }
    $$('[data-practice]').forEach(button => button.addEventListener('click', () => {
      const id = button.dataset.practice;
      state = { id, title: button.dataset.title, total: Number(button.dataset.duration) * 1000, remaining: 0, deadline: 0, mode: 'ready' };
      $('#practice-title').textContent = state.title;
      $('#practice-question').textContent = button.dataset.prompt;
      noteStatus.textContent = '';
      savedValue = '';
      let existing = '';
      try { existing = localStorage.getItem(storagePrefix + id) || ''; savedValue = existing; }
      catch { noteStatus.textContent = '此浏览器不允许本地存储。仍可临时书写并导出。'; }
      if (drafts.has(id)) { const draft = drafts.get(id); existing = draft.text; savedValue = draft.saved; }
      note.value = existing;
      resetTimer();
      openDialog(practiceDialog, toggle);
    }));
    toggle.addEventListener('click', () => {
      if (state.mode === 'running') {
        tick();
        if (state.mode === 'finished') return;
        clearInterval(interval);
        interval = null;
        state.mode = 'paused';
        toggle.textContent = '继续';
        setStatus(`已暂停，剩余 ${format(state.remaining)}。`);
      } else {
        if (state.mode === 'finished') state.remaining = state.total;
        state.mode = 'running';
        state.deadline = Date.now() + state.remaining;
        toggle.textContent = '暂停';
        tick();
        interval = setInterval(tick, 250);
      }
    });
    $('#timer-reset').addEventListener('click', resetTimer);
    document.addEventListener('visibilitychange', tick);
    $('#practice-close').addEventListener('click', () => practiceDialog.close());
    practiceDialog.addEventListener('close', () => { stashDraft(); clearInterval(interval); interval = null; state.mode = 'closed'; });
    note.addEventListener('input', () => {
      stashDraft();
      noteStatus.textContent = note.value === savedValue ? '' : '当前修改尚未保存；离开本页前可以保存或导出。';
    });
    $('#note-save').addEventListener('click', () => {
      try {
        localStorage.setItem(storagePrefix + state.id, note.value);
        savedValue = note.value;
        stashDraft();
        noteStatus.textContent = '已保存在此浏览器，没有上传。';
      } catch { noteStatus.textContent = '保存未成功。存储可能被禁用或已满，请使用“导出文字”。'; }
    });
    $('#note-export').addEventListener('click', () => {
      const file = new Blob([`${state.title}\n\n${note.value}\n`], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(file);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = `ways-home-${state.id}.txt`;
      document.body.append(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      noteStatus.textContent = '已生成文字文件。请确认文件保存成功；本浏览器记录不会因此改变。';
    });
    $('#note-clear').addEventListener('click', () => {
      if (!window.confirm('清除此练习在当前浏览器中的记录及本页草稿？其他练习不受影响。')) return;
      try {
        localStorage.removeItem(storagePrefix + state.id);
        note.value = '';
        savedValue = '';
        drafts.delete(state.id);
        noteStatus.textContent = '此项记录已清除。';
      } catch { noteStatus.textContent = '本地存储目前不可访问，未能确认删除；请在浏览器的网站数据设置中处理。'; }
    });
    window.addEventListener('beforeunload', event => {
      stashDraft();
      if ([...drafts.values()].some(draft => draft.text !== draft.saved)) { event.preventDefault(); event.returnValue = ''; }
    });
  }
})();
