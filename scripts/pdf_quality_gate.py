#!/usr/bin/env python3
"""Reproducible PDF structure/text/render checks; NOT a human visual sign-off."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "pdf/chatgpt-income-handbook-guide.pdf"
EDITION = ROOT / "pdf/edition.json"
OUT = ROOT / "pdf-qa-output"


def main() -> None:
    manifest = json.loads(EDITION.read_text(encoding="utf-8"))
    sha = hashlib.sha256(PDF.read_bytes()).hexdigest()
    assert sha == manifest["sha256"], "PDF/manifest hash mismatch"
    assert manifest["chapters"] == 34
    assert manifest["policy_reference_last_checked"] != manifest["edition_source_revision_date"], (
        "Do not relabel a policy review date as a PDF build date")
    OUT.mkdir(exist_ok=True)
    extracted = []
    images = []
    page_issues = []
    links = 0
    with fitz.open(PDF) as book:
        assert 40 <= book.page_count <= 250, f"Unexpected page count: {book.page_count}"
        assert "AI 酋长 Andy" in book.metadata.get("author", ""), "PDF author missing"
        for idx, page in enumerate(book):
            txt = page.get_text("text")
            extracted.append(txt)
            count = len(txt.strip())
            if idx > 0 and count < 10:
                page_issues.append(f"Page {idx+1}: empty/near-empty text")
            links += len(page.get_links())
            for block in page.get_text("blocks"):
                if len(block) < 5 or not str(block[4]).strip():
                    continue
                x0, y0, x1, y1 = block[:4]
                if x0 < -4 or y0 < -4 or x1 > page.rect.width + 4 or y1 > page.rect.height + 4:
                    page_issues.append(f"Page {idx+1}: text extends beyond media box {block[:4]}")
            # Every page is actually rasterised; previews are grouped for human QA.
            pix = page.get_pixmap(matrix=fitz.Matrix(.56, .56), alpha=False)
            images.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
        bookmarks = len(book.get_toc())
        fulltext = "".join(extracted)
        compact = "".join(fulltext.split())
        assert "AIPMAndy" in fulltext
        assert "metaver.vip" in fulltext
        assert "a6no1.cn" in fulltext
        assert "演示" in fulltext or "模拟" in fulltext
        for chapter in range(1, 35):
            assert f"第{chapter:02d}章" in compact, f"Source chapter {chapter:02d} absent from PDF"
        assert bookmarks >= 34, f"Missing navigable chapter bookmarks: {bookmarks}"
        assert links >= 20, f"Too few PDF links: {links}"
        assert not page_issues, "; ".join(page_issues[:15])

        cols, rows, pad, caption = 4, 4, 12, 24
        per_sheet = cols * rows
        width = max(im.width for im in images)
        height = max(im.height for im in images)
        for off in range(0, len(images), per_sheet):
            canvas = Image.new("RGB", (cols * (width + pad) + pad,
                                        rows * (height + pad + caption) + pad), "#e9eef3")
            draw = ImageDraw.Draw(canvas)
            for local, im in enumerate(images[off:off+per_sheet]):
                c, r = local % cols, local // cols
                x, y = pad + c * (width+pad), pad + r * (height+caption+pad)
                canvas.paste(im, (x, y))
                draw.text((x+2, y+height+5), f"Page {off+local+1}", fill="#384657")
            canvas.save(OUT / f"contact-{off//per_sheet+1:02d}.png", optimize=True)
        report = {"status": "automated-pass", "manual_hires_visual_review": "pending",
                  "real_iphone_android": "pending", "source_policy_refresh": "pending",
                  "sha256": sha, "pages": len(images), "chapter_count": 34,
                  "bookmarks": bookmarks, "links": links,
                  "text_chars": sum(len(t) for t in extracted),
                  "rendered_pages": len(images), "warnings": page_issues,
                  "contact_sheets": (len(images)+per_sheet-1)//per_sheet}
    (OUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n",
                                      encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"PDF quality gate failed: {e}", file=sys.stderr)
        raise
