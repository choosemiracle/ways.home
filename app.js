const menuToggle=document.querySelector('.menu-toggle');
const mobileNav=document.getElementById('mobileNav');

menuToggle?.addEventListener('click',()=>{
  const open=mobileNav.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded',String(open));
});

mobileNav?.querySelectorAll('a').forEach(link=>{
  link.addEventListener('click',()=>{
    mobileNav.classList.remove('open');
    menuToggle?.setAttribute('aria-expanded','false');
  });
});

const roadCards=[...document.querySelectorAll('.road-card')];
const lensNote=document.getElementById('lensNote');

const lensCopy={
  truth:{
    title:'求真：不是只有一种“知道”。',
    body:'科学强调公开可检验的证据与模型；哲学强调论证与概念澄清；历史学重建语境与证据链；第一人称传统研究体验本身。成熟的求真，不是让一种方法吞并所有问题，而是知道每一种认识方式能回答什么、不能回答什么。'
  },
  good:{
    title:'向善：从人格，到关系，再到制度。',
    body:'德性传统关心“成为怎样的人”，义务论关心不可逾越的规范，后果论衡量行动结果，照护伦理重视具体关系，政治与法律则处理陌生人如何在冲突中共同生活。'
  },
  beauty:{
    title:'近美：不仅是“好看”，而是重新训练感受力。',
    body:'美学可以研究和谐、比例与形式，也研究崇高、悲剧、丑与陌生化。艺术的力量常常不在于提供答案，而在于改变注意力，让被习惯遮住的世界重新显现。'
  },
  home:{
    title:'回归：同一个词，背后可能是完全不同的世界观。',
    body:'道家的归根、佛教的解脱、基督宗教的共融、苏菲的忆念、心理学的整合、生态学的相互依存不能简单画等号。它们共同回应“分裂感”，但对“谁在归、归向哪里、怎样归”的回答不同。'
  }
};

document.querySelectorAll('[data-lens]').forEach(button=>{
  button.addEventListener('click',()=>{
    const key=button.dataset.lens;
    const copy=lensCopy[key];
    lensNote.querySelector('h3').textContent=copy.title;
    lensNote.querySelector('p').textContent=copy.body;
    roadCards.forEach(card=>{
      card.classList.toggle('dimmed',!card.dataset.tags.includes(key));
    });
    document.querySelectorAll('.road-filter button').forEach(filterButton=>{
      filterButton.classList.toggle('active',filterButton.dataset.filter===key);
    });
    lensNote.scrollIntoView({behavior:'smooth',block:'center'});
  });
});

document.querySelectorAll('.road-filter button').forEach(button=>{
  button.addEventListener('click',()=>{
    const filter=button.dataset.filter;
    document.querySelectorAll('.road-filter button').forEach(item=>item.classList.remove('active'));
    button.classList.add('active');
    roadCards.forEach(card=>{
      const show=filter==='all'||card.dataset.tags.includes(filter);
      card.classList.toggle('dimmed',!show);
    });
  });
});