// 让外部链接在新标签页打开，避免用户离开你的主页。
// 只修改以 http 开头的链接（避免误伤站内锚点）。
const links = document.querySelectorAll('a[href^="http"]');

for (const link of links) {
  link.target = "_blank";               // 在新标签页打开
  link.rel = "noopener noreferrer";     // 安全与性能考虑
}
