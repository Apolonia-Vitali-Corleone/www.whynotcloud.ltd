// 显示最后更新时间
(function () {
  const el = document.getElementById('last-updated');
  if (!el) return;
  try {
    const d = new Date();
    const pad = (n)=> n.toString().padStart(2,'0');
    const ts = `${d.getFullYear()}.${pad(d.getMonth()+1)}.${pad(d.getDate())}`;
    el.textContent = ts;
  } catch (_) {}
})();

// 小交互：点击电话或邮箱自动复制
document.addEventListener('click', async (e) => {
  const a = e.target.closest('a');
  if (!a) return;
  const isTel = a.getAttribute('href')?.startsWith('tel:');
  const isMail = a.getAttribute('href')?.startsWith('mailto:');
  if (!isTel && !isMail) return;

  e.preventDefault(); // 不直接跳转，优先复制
  const text = isTel ? a.textContent.trim() : a.textContent.trim();
  try {
    await navigator.clipboard.writeText(text);
    toast(`已复制：${text}`);
    // 1.5 秒后再触发原动作（移动端仍可呼出拨号/邮件）
    setTimeout(() => { window.location.href = a.href; }, 1500);
  } catch {
    window.location.href = a.href;
  }
});

// 轻量提示
function toast(msg){
  const t = document.createElement('div');
  t.textContent = msg;
  Object.assign(t.style, {
    position:'fixed', left:'50%', bottom:'28px', transform:'translateX(-50%)',
    background:'rgba(0,0,0,.7)', color:'#fff', padding:'10px 14px',
    borderRadius:'10px', fontSize:'14px', zIndex:9999, backdropFilter:'blur(6px)'
  });
  document.body.appendChild(t);
  setTimeout(()=> t.remove(), 1600);
}
