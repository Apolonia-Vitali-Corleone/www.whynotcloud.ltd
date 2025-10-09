// 切换到中文：跳转到提供的中文地址
const zhUrl = "https://cv.whynotcloud.ltd/cn/index.html";

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("lang-toggle");
  if (btn) {
    btn.addEventListener("click", () => {
      window.location.href = zhUrl;
    });
  }
});
