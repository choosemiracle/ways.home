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

const recommendation=document.getElementById('recommendation');
const wayCards=[...document.querySelectorAll('.way-card')];

const pathCopy={
  self:{
    title:'先从“听见自己”开始。',
    body:'可以从帕克·帕尔默进入，再走向信任圈与贵格会传统：先辨认生命里真正重要的东西，再学习让这种内在感受接受关系、时间与行动的检验。'
  },
  relation:{
    title:'先练习：靠近，而不接管。',
    body:'可以从二人聆听开始，再进入信任圈与鲁米。重点不是更快理解对方，而是少一点解释和修理，让一个人仍然拥有自己的经验。'
  },
  group:{
    title:'先看看“共同中心”是什么。',
    body:'可以从共同等候进入，再延伸到贵格会、信任圈与 Pendle Hill：一群人如何在不争夺中心的前提下，形成更深的共同辨识。'
  },
  poetry:{
    title:'先让第三物说话。',
    body:'从鲁米、诗歌、电影与故事进入，再回到信任圈的第三物实践。先不解释作者，也不急着总结，只留意：它在我里面唤起了什么？'
  },
  life:{
    title:'让内在工作接受现实检验。',
    body:'可以从帕尔默与 Pendle Hill 开始，再进入贵格会的“内在—外在”传统。真正的看见，最终会改变工作、关系、选择与共同生活。'
  },
  practice:{
    title:'先做一次，再决定往哪里走。',
    body:'从 3 分钟静默、11 分钟二人聆听或 12 分钟共同等候开始。经验之后，再回到相应传统理解它的来源、边界与方法。'
  }
};

document.querySelectorAll('[data-path]').forEach(card=>{
  card.addEventListener('click',()=>{
    const key=card.dataset.path;
    const copy=pathCopy[key];
    recommendation.querySelector('h3').textContent=copy.title;
    recommendation.querySelector('p').textContent=copy.body;
    wayCards.forEach(way=>{
      way.classList.toggle('dimmed',!way.dataset.tags.includes(key));
    });
    recommendation.scrollIntoView({behavior:'smooth',block:'center'});
  });
});

const pauseBtn=document.getElementById('pauseBtn');
const timerPanel=document.getElementById('timerPanel');
const timerDisplay=document.getElementById('timerDisplay');
const timerCancel=document.getElementById('timerCancel');

let timer=null;

function formatTime(seconds){
  const minutes=String(Math.floor(seconds/60)).padStart(2,'0');
  const remaining=String(seconds%60).padStart(2,'0');
  return minutes+':'+remaining;
}

function startTimer(seconds){
  clearInterval(timer);
  let remaining=seconds;
  timerDisplay.textContent=formatTime(remaining);
  timerPanel.hidden=false;

  timer=setInterval(()=>{
    remaining-=1;
    timerDisplay.textContent=formatTime(Math.max(0,remaining));
    if(remaining<=0){
      clearInterval(timer);
      timerDisplay.textContent='00:00';
    }
  },1000);
}

pauseBtn?.addEventListener('click',()=>startTimer(60));
document.querySelectorAll('[data-timer]').forEach(button=>{
  button.addEventListener('click',()=>startTimer(Number(button.dataset.timer)));
});
timerCancel?.addEventListener('click',()=>{
  clearInterval(timer);
  timerPanel.hidden=true;
});
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'&&!timerPanel.hidden){
    clearInterval(timer);
    timerPanel.hidden=true;
  }
});