/* 洪盛集藏二维码显示兼容层：保留原始二维码，不生成替代二维码。 */
(function(){
  function fix(img){
    if(!img || img.dataset.qrFixed) return;
    img.dataset.qrFixed='1';
    var src=img.getAttribute('src');
    if(!src) return;
    img.addEventListener('error',function(){
      img.classList.add('qr-load-error');
      img.alt='客服二维码暂时无法加载，请稍后刷新';
    },{once:true});
    img.addEventListener('load',function(){img.classList.remove('qr-load-error')},{once:true});
  }
  function scan(){document.querySelectorAll('img[src*="qr-service"]').forEach(fix)}
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',scan); else scan();
  new MutationObserver(scan).observe(document.documentElement,{childList:true,subtree:true});
})();
