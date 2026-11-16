#!/usr/bin/env python3
"""Build a source-driven Chinese handbook PDF; no invented commercial outcomes.

Input: the canonical 34-chapter Markdown and named public SOP, sample, sources
and templates. All examples retain their original provenance labels.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import quote

from markdown import markdown
from weasyprint import HTML

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://github.com/AIPMAndy/chatgpt-income-handbook"
SITE = "https://aipmandy.github.io/chatgpt-income-handbook/"
OUTPUT = ROOT / "pdf/chatgpt-income-handbook-guide.pdf"
SOURCE = ROOT / "docs/COMPLETE-GUIDE.md"
APPENDICES = [
    "docs/SERVICE-SOPS.md",
    "docs/END-TO-END-TRIAL.md",
    "docs/DEMO-CASE-LAB.md",
    "docs/UNIT-ECONOMICS.md",
    "docs/PRIVACY-SOP.md",
    "docs/EVIDENCE-PUBLICATION.md",
    "docs/QUALITY-METHOD.md",
    "docs/SOURCES.md",
    "guides/7-DAY-PLAN.md",
    "guides/30-DAY-PLAN.md",
]
APPENDICES += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "templates").glob("*.md"))]


def revision_date() -> str:
    # Source revision, not a fictional "today we checked the policy" date.
    try:
        return subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", str(SOURCE.relative_to(ROOT)),
             "scripts/build_pdf.py"], cwd=ROOT, text=True
        ).strip() or "2026-11-16"
    except (OSError, subprocess.CalledProcessError):
        return "2026-11-16"


def source_url(path: Path) -> str:
    return BASE + "/blob/main/" + quote(path.relative_to(ROOT).as_posix(), safe="/")


def html_from_md(content: str, origin: Path) -> str:
    rendered = markdown(content, extensions=["extra", "sane_lists", "toc"])
    # Static Markdown has links; convert local references to verifiable repository
    # URLs so a downloaded PDF never contains broken relative .md destinations.
    def replace(m: re.Match) -> str:
        href = html.unescape(m.group(1))
        if href.startswith(("#", "https://", "http://", "mailto:")):
            return m.group(0)
        target = (origin.parent / href.split("#")[0].split("?")[0]).resolve()
        if not target.is_relative_to(ROOT):
            return 'href="' + BASE + '"'
        anchor = "#" + href.split("#", 1)[1] if "#" in href else ""
        return 'href="' + source_url(target) + anchor + '"'
    return re.sub(r'href="([^"]+)"', replace, rendered)


def source_section(path: Path, serial: int) -> str:
    md = path.read_text(encoding="utf-8")
    tag = "REUSABLE TEMPLATE" if "templates/" in path.as_posix() else "REFERENCE / SOP"
    return (
        f'<section class="chapter"><p class="kicker">{tag} · {serial:02d}</p>'
        f'<div class="md">{html_from_md(md, path)}</div>'
        '<p class="provenance">可编辑原文 / SOURCE: '
        f'<a href="{source_url(path)}">{html.escape(path.relative_to(ROOT).as_posix())}</a>'
        '</p></section>'
    )


STYLE = r"""
@page { size:A4; margin:19mm 19mm 20mm 19mm;
  @bottom-left { content:"AI 酋长 Andy  /  独立开源知识"; font:8pt "Noto Sans CJK SC",sans-serif; color:#7c8796; }
  @bottom-right { content:counter(page); font:9pt sans-serif; color:#7c8796; }
}
@page:first { @bottom-left {content:none;} @bottom-right {content:none;} }
* { box-sizing:border-box; }
body { font-family:"Noto Sans CJK SC","Noto Sans SC",sans-serif;
  color:#172435; font-size:9.9pt; line-height:1.7; }
a { color:#215b8e; text-decoration:none; }
p,li { orphans:3; widows:3; }
.cover { page-break-after:always; min-height:244mm; padding:20mm 0 0; }
.logo { color:#1b3656; font-size:10pt; font-weight:700; letter-spacing:2px;
  border-bottom:1px solid #c5d2df; padding-bottom:8mm; }
.overline { margin-top:40mm; color:#547495; font-size:10pt; letter-spacing:2px; }
.cover h1 { font-size:38pt; line-height:1.28; letter-spacing:-1px; margin:7mm 0 7mm; color:#12273e; }
.cover .deck { max-width:146mm; font-size:14pt; color:#38526c; margin-bottom:12mm; }
.accent { display:block; width:26mm; height:2mm; background:#285f91; }
.cover .note { margin-top:16mm; max-width:145mm; color:#5a6b7b; line-height:2; font-size:10.5pt; }
.contacts { border-top:1px solid #cbd7e1; margin-top:39mm; padding-top:8mm; font-size:9.3pt; }
.contacts strong { color:#16476a; }
.toc { page-break-after:always; }
.toc h2 { font-size:23pt; color:#17283b; margin:11mm 0 3mm; }
.toc p { color:#627488; margin:0 0 9mm; }
.toc-grid { columns:2; column-gap:10mm; }
.toc-grid a { display:block; break-inside:avoid; font-size:9pt; line-height:1.65;
  padding:1.9mm 0; border-bottom:1px solid #e1e9f1; color:#263e57; }
.toc-grid b { margin-right:2mm; color:#436b94; }
.toc .callout { margin-top:9mm; background:#f0f5fa; padding:4mm;
  border-left:2mm solid #366b9b; font-size:9pt; }
.chapter { page-break-before:always; }
.kicker { color:#567a9f; font-size:8pt; letter-spacing:1.5px; font-weight:bold;
  border-bottom:1px solid #d7e2ec; padding-bottom:4mm; }
.md h1 { color:#15314a; font-size:21pt; line-height:1.35; margin:8mm 0 5mm;
  page-break-after:avoid; }
.md h2 { color:#193d5f; font-size:17pt; line-height:1.4; margin:8mm 0 4mm;
  page-break-after:avoid; }
.md h3 { color:#20496c; font-size:12pt; margin:7mm 0 3mm; page-break-after:avoid; }
.md p { margin:2.5mm 0 3.5mm; }
.md ol,.md ul { padding-left:6mm; }
.md li { margin:1.6mm 0; }
.md blockquote { margin:5mm 0; padding:3mm 5mm;
  border-left:2px solid #5a83ab; background:#eff4f9; color:#415e77; }
.md pre { background:#f5f7fa; border:1px solid #dbe4ec; padding:4mm;
  font:8pt monospace; white-space:pre-wrap; overflow-wrap:anywhere; }
.md code { font:8.2pt monospace; background:#f1f5f9; padding:.2mm 1mm;
  overflow-wrap:anywhere; }
.md table { border-collapse:collapse; width:100%; font-size:8pt; table-layout:fixed; }
.md td,.md th { border:1px solid #d6e1eb; padding:2mm; overflow-wrap:anywhere; }
.md th { background:#edf4fa; }
.provenance { border-top:1px solid #dce5ed; margin-top:9mm; padding-top:4mm;
  color:#768695; font-size:8pt; overflow-wrap:anywhere; }
.appendix { page-break-before:always; padding-top:39mm; }
.appendix h2 { font-size:29pt; color:#1b3651; }
.appendix p { color:#5e7080; }
.last { page-break-before:always; padding-top:15mm; }
.last h2 { font-size:24pt; color:#183552; }
.last a { overflow-wrap:anywhere; }
"""


def main() -> None:
    raw = SOURCE.read_text(encoding="utf-8")
    chunks = re.split(r"(?=^## 第\d{2}章)", raw, flags=re.M)
    chapters = [part for part in chunks if re.match(r"^## 第\d{2}章", part)]
    assert len(chapters) == 34, f"Expected 34 canonical Markdown chapters, found {len(chapters)}"
    assert all((ROOT / p).is_file() for p in APPENDICES)
    date = revision_date()
    navigation, bodies = [], []
    for index, content in enumerate(chapters, 1):
        title = content.splitlines()[0].lstrip("# ").strip()
        navigation.append(f'<a href="#chapter-{index:02d}"><b>{index:02d}</b>{html.escape(title)}</a>')
        bodies.append(
            f'<section class="chapter" id="chapter-{index:02d}">'
            f'<p class="kicker">CHAPTER / {index:02d} OF 34</p>'
            f'<div class="md">{html_from_md(content, SOURCE)}</div>'
            '<p class="provenance">原文及后续修订：'
            f'<a href="{source_url(SOURCE)}">docs/COMPLETE-GUIDE.md</a></p></section>'
        )
    sources = ''.join(source_section(ROOT / p, n) for n, p in enumerate(APPENDICES, 1))
    document = (
        '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
        '<title>ChatGPT 商业实践手册｜34章开源攻略</title>'
        '<meta name="author" content="AI 酋长 Andy / 星觉科技">'
        '<meta name="description" content="34章教程、交付SOP、教学模拟、案例证据和公开模板">'
        '<meta name="keywords" content="ChatGPT, AI, 商业实践, AI酋长Andy, 星觉科技">'
        '<style>'
        + STYLE + '</style></head><body>'
        '<section class="cover">'
        '<div class="logo">星觉科技 / XINGJUE KNOWLEDGE</div>'
        f'<p class="overline">OPEN SOURCE EDITION · {html.escape(date)}</p>'
        '<h1>ChatGPT<br>商业实践手册</h1>'
        '<p class="deck">从一个具体问题，到第一份可验收的服务。</p>'
        '<span class="accent"></span>'
        '<p class="note">34 章源文档驱动的完整教程，附服务 SOP、演示案例、'
        '交付质量与隐私规则、官方资料入口、行动计划和开放模板。'
        '模拟案例均为教学，不是客户真实交易；不提供收入承诺。</p>'
        '<div class="contacts"><strong>AI 酋长 Andy</strong> · 星觉科技<br>'
        '微信：AIPMAndy · <a href="https://metaver.vip/">个人官网</a> · '
        '<a href="https://www.a6no1.cn/">公司官网</a><br>'
        '<a href="https://metaver.vip/services">咨询与陪跑服务</a> · '
        f'<a href="{SITE}">在线互动版</a> · <a href="{BASE}">开源原文</a></div></section>'
        '<section class="toc"><h2>阅读地图</h2>'
        '<p>建议先读定位与验证，选定一项服务，再用交付模板去验证。'
        '章节编号为学习结构，不代表保证收入的步骤。</p>'
        '<div class="toc-grid">' + ''.join(navigation) + '</div>'
        '<div class="callout">附录提供范围说明、风险与版权、授权检查、'
        '成本计算、来源台账及可编辑模板。来源台账最近记录为 2026-10-22；'
        '动态政策必须通过官方原文重新核对。</div></section>'
        + ''.join(bodies)
        + '<section class="appendix"><p class="kicker">APPENDIX / REPRODUCIBLE MATERIALS</p>'
        '<h2>开放附录与可编辑模板</h2>'
        '<p>资料完整保留原有模拟、作者自述与证据分级标识。每份文档末尾均附 GitHub 原文链接。'
        '动态政策、收费、平台功能和案例许可请自行复核。</p></section>'
        + sources
        + '<section class="last"><p class="kicker">CONTACT / SOURCE</p>'
        '<h2>持续更新，始终可核验。</h2>'
        '<p>本文档和网站完全免费；需要具体项目的 AI 产品化、职业成长或内容获客咨询，'
        '可通过下面的公开入口了解适用范围和服务边界。</p>'
        '<p><b>个人微信：</b>AIPMAndy</p>'
        '<p><b>个人官网：</b><a href="https://metaver.vip/">https://metaver.vip/</a></p>'
        '<p><b>公司官网：</b><a href="https://www.a6no1.cn/">https://www.a6no1.cn/</a></p>'
        '<p><b>服务入口：</b><a href="https://metaver.vip/services">https://metaver.vip/services</a></p>'
        f'<p><b>开源仓库：</b><a href="{BASE}">{BASE}</a></p>'
        '<p>所有金额、报价与成本模型用于教学，不构成保证。'
        '不提供财税、法律或投资意见；资料和政策请根据官方来源复核。</p>'
        '</section></body></html>'
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    # Fixed PDF identifier avoids time/random IDs changing otherwise identical editions.
    source_fingerprint = hashlib.sha256(
        (raw + "\n" + "".join((ROOT / p).read_text(encoding="utf-8") for p in APPENDICES)
        ).encode("utf-8")
    ).hexdigest()
    HTML(string=document, base_url=str(ROOT)).write_pdf(
        str(OUTPUT), pdf_identifier="chatgpt-income-handbook-" + source_fingerprint
    )
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    edition = {
        "title": "ChatGPT 商业实践手册",
        "pdf": OUTPUT.relative_to(ROOT).as_posix(),
        "sha256": digest,
        "source": "docs/COMPLETE-GUIDE.md",
        "chapters": len(chapters),
        "appendices": APPENDICES,
        "edition_source_revision_date": date,
        "policy_reference_last_checked": "2026-10-22",
        "provenance": "repository Markdown; demos are educational only",
    }
    (OUTPUT.parent / "edition.json").write_text(
        json.dumps(edition, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"pdf": str(OUTPUT.relative_to(ROOT)), "sha256": digest,
                      "chapters": len(chapters), "appendices": len(APPENDICES)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
