/* Generated with the same editorial plans used by the Python renderer.
 * Only updates headings inserted/changed by search, comparisons and dialogs.
 * All static headings already work without JavaScript. */
(() => {
  'use strict';
  const plans = __HEADING_PLANS__;
  const selector = 'h1,h2,h3';
  const remembered = new WeakMap();
  const headings = root => {
    const list = [...(root.querySelectorAll?.(selector) || [])];
    if (root.matches?.(selector)) list.unshift(root);
    return list;
  };
  function format(heading) {
    const text = heading.textContent;
    if (!text || remembered.get(heading) === text) return;
    remembered.set(heading, text);
    const suffix = text.match(/\s*[↗→↑]$/)?.[0] || '';
    const core = suffix ? text.slice(0, -suffix.length) : text;
    const reviewed = Object.hasOwn(plans, core);
    const clauses = reviewed ? plans[core] : (core.match(/[^，；：。！？]+[，；：。！？]*|[，；：。！？]+/g) || [core]).map(s => [s]);
    const output = document.createDocumentFragment();
    clauses.forEach((units, ci) => {
      if (ci) output.append(document.createElement('wbr'));
      const clause = document.createElement('span');
      clause.className = 'title-clause';
      units.forEach((text, ui) => {
        if (ui) clause.append(document.createElement('wbr'));
        const unit = document.createElement('span');
        unit.className = 'title-unit' + (!reviewed && text.length > 9 ? ' title-unit--fluid' : '');
        unit.textContent = text;
        if (suffix && ci === clauses.length - 1 && ui === units.length - 1) {
          const endmark = document.createElement('span');
          endmark.className = 'title-endmark';
          endmark.setAttribute('aria-hidden', 'true');
          endmark.textContent = suffix;
          unit.append(endmark);
        }
        clause.append(unit);
      });
      output.append(clause);
    });
    const target = heading.children.length === 1 && heading.firstElementChild.tagName === 'A' ? heading.firstElementChild : heading;
    target.replaceChildren(output);
    heading.classList.remove('title--short', 'title--medium', 'title--long');
    heading.classList.add('title-flow', core.length >= 20 ? 'title--long' : core.length >= 13 ? 'title--medium' : 'title--short');
  }
  headings(document).forEach(heading => {
    if (heading.classList.contains('title-flow')) remembered.set(heading, heading.textContent);
    else format(heading);
  });
  new MutationObserver(records => {
    const pending = new Set();
    for (const record of records) {
      const parent = record.target.nodeType === Node.ELEMENT_NODE ? record.target : record.target.parentElement;
      const owner = parent?.closest(selector);
      if (owner) pending.add(owner);
      for (const node of record.addedNodes) if (node.nodeType === Node.ELEMENT_NODE) headings(node).forEach(h => pending.add(h));
    }
    pending.forEach(format);
  }).observe(document.body, { childList: true, characterData: true, subtree: true });
})();
