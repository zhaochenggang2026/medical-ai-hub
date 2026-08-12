#!/usr/bin/env python3
"""
医疗AI前沿 网站自动更新脚本
从 Obsidian 知识库抓取最新文章 → 生成 HTML 页面 → 推送到 GitHub Pages
用法: python3 build_site.py
"""
import os
import re
import html
import datetime
import subprocess
import glob

# ========== 配置 ==========
VAULT_DIR = os.path.expanduser("~/obsidian-zhaochenggang")
ARTICLE_DIR = os.path.join(VAULT_DIR, "Outputs/1-技术方案")
SITE_DIR = os.path.expanduser("~/website-demo")
# GitHub 仓库（token 通过环境变量 GITHUB_TOKEN 提供，避免密钥入库）
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = f"https://x-access-token:{GITHUB_TOKEN}@github.com/zhaochenggang2026/medical-ai-hub.git" if GITHUB_TOKEN else "https://github.com/zhaochenggang2026/medical-ai-hub.git"
MAX_ARTICLES = 8  # 首页显示文章数

# 排除的文件（非文章）
EXCLUDE = [
    "cover-", "MultiPost", "小红书发布进度", "小红书发布文档清单",
    "封面", "发布包", "README",
]

def get_articles():
    """扫描文章目录，返回按时间排序的文章列表"""
    articles = []
    for f in sorted(glob.glob(os.path.join(ARTICLE_DIR, "*.md"))):
        name = os.path.basename(f)
        if any(e in name for e in EXCLUDE):
            continue
        # 提取标题（第一个 # 或文件名）
        try:
            with open(f, encoding="utf-8") as fh:
                content = fh.read()
        except Exception:
            continue
        m = re.search(r"^#\s+(.+)$", content, re.M)
        title = m.group(1).strip() if m else name.replace(".md", "").replace("_", " ")
        # 提取摘要（第一个段落）
        para = re.search(r"\n\n(.+?)\n\n", content, re.S)
        summary = html.escape(para.group(1).strip()[:120]) if para else ""
        # 提取日期
        mdate = re.search(r"created:\s*(\d{4}-\d{2}-\d{2})", content)
        date = mdate.group(1) if mdate else datetime.date.today().isoformat()
        # 生成文章ID
        aid = re.sub(r"[^\w\u4e00-\u9fff]", "-", title)[:30]
        articles.append({
            "title": title, "summary": summary, "date": date,
            "file": name, "aid": aid,
        })
    # 按日期倒序
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles

def build_index(articles):
    """生成首页 HTML"""
    top = articles[0] if articles else None
    rest = articles[1:MAX_ARTICLES] if len(articles) > 1 else []

    posts_html = ""
    if top:
        posts_html += f'''<div class="post">
    <div class="date">{top['date']} · 自动生成</div>
    <h3>{html.escape(top['title'])}</h3>
    <p>{top['summary']}…</p>
    <a href="posts/{top['aid']}.html">阅读全文 →</a>
  </div>'''
    for a in rest:
        posts_html += f'''<div class="post">
    <div class="date">{a['date']} · 自动生成</div>
    <h3>{html.escape(a['title'])}</h3>
    <p>{a['summary']}…</p>
    <a href="posts/{a['aid']}.html">阅读全文 →</a>
  </div>'''

    total = len(articles)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>医疗AI前沿 | 医疗器械工程师的AI情报站</title>
<meta name="description" content="专注医疗器械AI落地：算法、平台、法规、案例">
<style>
:root {{ --bg:#0f172a; --card:#1e293b; --text:#e2e8f0; --accent:#38bdf8; --green:#4ade80; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); line-height:1.7; }}
.container {{ max-width:900px; margin:0 auto; padding:20px; }}
header {{ padding:60px 0 30px; text-align:center; }}
h1 {{ font-size:2.4em; background:linear-gradient(135deg,var(--accent),var(--green)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.tagline {{ color:#94a3b8; margin-top:10px; }}
.badge {{ display:inline-block; background:var(--card); border:1px solid #334155; padding:4px 14px; border-radius:20px; font-size:.85em; margin:15px 4px 0; color:var(--accent); }}
.stats {{ display:flex; justify-content:center; gap:40px; margin-top:20px; }}
.stat .num {{ font-size:1.8em; font-weight:bold; color:var(--green); }}
.stat .label {{ color:#64748b; font-size:.8em; }}
.post {{ background:var(--card); border-radius:12px; padding:18px 20px; margin-bottom:12px; border:1px solid #334155; }}
.post .date {{ color:var(--green); font-size:.8em; }}
.post h3 {{ margin:6px 0; }}
.post p {{ color:#94a3b8; font-size:.9em; }}
.post a {{ color:var(--accent); text-decoration:none; }}
h2 {{ color:var(--accent); margin:25px 0 12px; }}
.auto {{ text-align:center; color:#64748b; font-size:.8em; padding:30px 0; border-top:1px solid #334155; margin-top:30px; }}
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>🧠 医疗AI前沿</h1>
    <div class="tagline">医疗器械工程师的 AI 情报站 · 由 Hermes Agent 自动运营</div>
    <div><span class="badge">算法</span><span class="badge">平台</span><span class="badge">法规</span><span class="badge">案例</span></div>
    <div class="stats">
      <div class="stat"><div class="num">{total}</div><div class="label">已发文章</div></div>
      <div class="stat"><div class="num">7×24</div><div class="label">自动运营</div></div>
    </div>
  </header>
  <h2>📌 最新文章</h2>
  {posts_html}
  <div class="auto">⚡ 本站由 Hermes Agent 自动生成与运营 · 内容定时更新 · 全程无需手写代码<br>最近更新：{datetime.date.today().isoformat()}</div>
</div>
</body>
</html>'''

def build_post(article):
    """生成单篇文章页"""
    # 读取正文并转 HTML（简单转换：段落 + 标题 + 代码块）
    try:
        with open(os.path.join(ARTICLE_DIR, article["file"]), encoding="utf-8") as fh:
            content = fh.read()
    except Exception:
        content = ""
    # 去掉 frontmatter
    content = re.sub(r"^---\n.*?\n---\n", "", content, flags=re.S)
    # 转 HTML
    lines = content.split("\n")
    body = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            if in_code:
                body.append("</pre>")
                in_code = False
            else:
                body.append("<pre>")
                in_code = True
            continue
        if in_code:
            body.append(html.escape(line))
            continue
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("**") and line.endswith("**") and len(line) < 60:
            body.append(f"<h4>{html.escape(line.strip('*'))}</h4>")
        elif line.startswith("|"):
            body.append(f"<p class='table'>{html.escape(line)}</p>")
        elif line.startswith("- ") or line.startswith("* "):
            body.append(f"<p class='li'>• {html.escape(line[2:])}</p>")
        else:
            body.append(f"<p>{html.escape(line)}</p>")
    body_html = "\n".join(body)

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(article['title'])} | 医疗AI前沿</title>
<style>
:root {{ --bg:#0f172a; --card:#1e293b; --text:#e2e8f0; --accent:#38bdf8; --green:#4ade80; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif; background:var(--bg); color:var(--text); line-height:1.8; }}
.container {{ max-width:800px; margin:0 auto; padding:30px 20px; }}
h1 {{ font-size:1.8em; color:var(--accent); margin-bottom:10px; }}
h2 {{ color:var(--accent); margin:25px 0 10px; }}
h3 {{ color:var(--green); margin:20px 0 8px; }}
p {{ margin:10px 0; color:#cbd5e1; }}
pre {{ background:#0b1120; border:1px solid #334155; border-radius:8px; padding:15px; overflow-x:auto; font-size:.85em; color:#7dd3fc; }}
.back {{ display:inline-block; margin:20px 0; color:var(--accent); text-decoration:none; }}
.date {{ color:var(--green); font-size:.85em; }}
.auto {{ text-align:center; color:#64748b; font-size:.8em; margin-top:40px; padding-top:20px; border-top:1px solid #334155; }}
</style>
</head>
<body>
<div class="container">
  <a class="back" href="../index.html">← 返回首页</a>
  <div class="date">{article['date']} · 自动生成</div>
  {body_html}
  <div class="auto">⚡ 由 Hermes Agent 自动生成</div>
</div>
</body>
</html>'''

def main():
    articles = get_articles()
    if not articles:
        print("❌ 未找到文章")
        return

    # 生成首页
    index_html = build_index(articles)
    with open(os.path.join(SITE_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # 生成文章页
    posts_dir = os.path.join(SITE_DIR, "posts")
    os.makedirs(posts_dir, exist_ok=True)
    count = 0
    for a in articles[:MAX_ARTICLES]:
        post_html = build_post(a)
        with open(os.path.join(posts_dir, f"{a['aid']}.html"), "w", encoding="utf-8") as f:
            f.write(post_html)
        count += 1

    print(f"✅ 生成完成：首页 + {count} 篇文章页（共 {len(articles)} 篇文章）")

    # 推送 GitHub
    os.chdir(SITE_DIR)
    subprocess.run(["git", "add", "-A"], capture_output=True)
    subprocess.run(["git", "-c", "user.name=Hermes-Agent",
                    "-c", "user.email=hermes@nousresearch.com",
                    "commit", "-m", f"auto update {datetime.date.today().isoformat()}"],
                   capture_output=True)
    r = subprocess.run(["git", "push", "-f", GITHUB_REPO, "HEAD:master"],
                       capture_output=True, text=True, timeout=60)
    if r.returncode == 0 or "Everything up-to-date" in r.stderr:
        print("✅ 已推送到 GitHub Pages")
    else:
        print(f"⚠️ 推送输出: {r.stderr[-200:]}")

if __name__ == "__main__":
    main()
