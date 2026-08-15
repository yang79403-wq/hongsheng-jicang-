const grid=document.getElementById('marketGrid');
const updated=document.getElementById('updated');
function money(v){return v==null?'待接入':('¥'+Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2}))}
async function load(cat=''){
  grid.innerHTML='<div class="muted">正在加载行情…</div>';
  const url='/api/prices'+(cat?'?category='+encodeURIComponent(cat):'');
  try{
    const res=await fetch(url); const data=await res.json();
    if(!data.length){grid.innerHTML='<div class="muted">暂无该分类数据，等待自动采集。</div>';return}
    grid.innerHTML=data.map(x=>`<article class="market"><div class="name">${x.name}</div><div class="price">${money(x.price)}</div><div class="${x.change_pct>0?'up':''}">${x.price==null?'市场参考价待更新':(x.change_pct>0?'↑ ':'')+x.change_pct+'%'}</div><div class="source">${x.source||'数据源'} · ${x.captured_at||''}</div></article>`).join('');
    updated.textContent='数据状态：自动化行情接口已连接';
  }catch(e){grid.innerHTML='<div class="muted">行情接口暂不可用，请稍后刷新。</div>';updated.textContent='数据接口离线';}
}
document.querySelectorAll('.filters button').forEach(btn=>btn.addEventListener('click',()=>{document.querySelectorAll('.filters button').forEach(b=>b.classList.remove('active'));btn.classList.add('active');load(btn.dataset.cat);}));
load();
