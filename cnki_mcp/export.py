"""
批量导出工具。

支持 4 种导出格式：
- json: 格式化 JSON
- csv: CSV 表格
- bibtex: BibTeX (.bib)
- ris: RIS (.ris)

纯逻辑模块，不需要浏览器。
"""

import csv
import io
import json as json_mod

from cnki_mcp.exceptions import ExportError

SUPPORTED_FORMATS = ["csv", "json", "bibtex", "ris"]


def _make_bibtex_key(title: str, authors: list[str], year: str, index: int = 0) -> str:
    """生成 BibTeX 引用键"""
    # 取第一作者姓氏拼音 + 年份
    if authors:
        first_author = authors[0].split("(")[0].strip()
        # 提取拼音部分
        name_parts = first_author.split()
        if name_parts:
            last = name_parts[-1].lower()
            # 简单过滤非字母字符
            last = "".join(c for c in last if c.isalpha())
            if last:
                return f"{last}{year or 'xxxx'}"
    return f"ref{index + 1}"


def _escape_bibtex(text: str) -> str:
    """转义 BibTeX 特殊字符"""
    return text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")


def _escape_ris(text: str) -> str:
    """转义 RIS 特殊字符"""
    return text.replace("\n", " ").replace("\r", "")


def export_json(papers: list[dict]) -> str:
    """导出为格式化的 JSON"""
    return json_mod.dumps(papers, ensure_ascii=False, indent=2)


def export_csv(papers: list[dict]) -> str:
    """导出为 CSV"""
    if not papers:
        return ""
    output = io.StringIO()
    fieldnames = ["title", "authors", "source", "date", "year", "volume", "issue", "pages", "doi", "cited_count", "download_count"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for p in papers:
        row = dict(p)
        if isinstance(row.get("authors"), list):
            row["authors"] = "; ".join(row["authors"])
        writer.writerow(row)
    return output.getvalue()


def export_bibtex(papers: list[dict]) -> str:
    """导出为 BibTeX"""
    entries = []
    for i, p in enumerate(papers):
        authors = p.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(";")]
        author_str = " and ".join(a.split("(")[0].strip() for a in authors)

        key = _make_bibtex_key(p.get("title", ""), authors, p.get("year", ""), i)
        entry = f"@article{{{key},\n"
        if author_str:
            entry += f"  author = {{{_escape_bibtex(author_str)}}},\n"
        entry += f"  title = {{{_escape_bibtex(p.get('title', ''))}}},\n"
        if p.get("source"):
            entry += f"  journal = {{{_escape_bibtex(p['source'])}}},\n"
        if p.get("year"):
            entry += f"  year = {{{p['year']}}},\n"
        if p.get("volume"):
            entry += f"  volume = {{{p['volume']}}},\n"
        if p.get("issue"):
            entry += f"  number = {{{p['issue']}}},\n"
        if p.get("pages"):
            entry += f"  pages = {{{p['pages']}}},\n"
        if p.get("doi"):
            entry += f"  doi = {{{p['doi']}}},\n"
        entry += "}\n"
        entries.append(entry)
    return "\n".join(entries)


def export_ris(papers: list[dict]) -> str:
    """导出为 RIS"""
    entries = []
    for p in papers:
        lines = ["TY  - JOUR"]
        authors = p.get("authors", [])
        if isinstance(authors, str):
            authors = [a.strip() for a in authors.split(";")]
        for a in authors:
            lines.append(f"AU  - {_escape_ris(a.split('(')[0].strip())}")
        lines.append(f"TI  - {_escape_ris(p.get('title', ''))}")
        if p.get("source"):
            lines.append(f"JO  - {_escape_ris(p['source'])}")
        if p.get("year"):
            lines.append(f"PY  - {p['year']}//")
        if p.get("volume"):
            lines.append(f"VL  - {p['volume']}")
        if p.get("issue"):
            lines.append(f"IS  - {p['issue']}")
        if p.get("pages"):
            lines.append(f"SP  - {p['pages'].split('-')[0] if '-' in p.get('pages', '') else p['pages']}")
            if "-" in p.get("pages", ""):
                lines.append(f"EP  - {p['pages'].split('-')[1]}")
        if p.get("doi"):
            lines.append(f"DO  - {p['doi']}")
        lines.append("ER  - ")
        entries.append("\n".join(lines))
    return "\n".join(entries)


EXPORTERS = {
    "csv": export_csv,
    "json": export_json,
    "bibtex": export_bibtex,
    "ris": export_ris,
}

EXTENSIONS = {
    "csv": ".csv",
    "json": ".json",
    "bibtex": ".bib",
    "ris": ".ris",
}


def export_papers_impl(papers_data: str, fmt: str = "json") -> dict:
    """导出核心逻辑"""
    fmt = fmt.lower().strip()
    if fmt not in EXPORTERS:
        raise ExportError(
            f"不支持的导出格式: {fmt}。支持: {', '.join(SUPPORTED_FORMATS)}"
        )

    try:
        papers = json_mod.loads(papers_data)
    except json_mod.JSONDecodeError as e:
        raise ExportError(f"论文数据 JSON 解析失败: {e}")

    if not isinstance(papers, list):
        raise ExportError("论文数据必须是列表（数组）")

    if not papers:
        return {"format": fmt, "count": 0, "content": "", "filename": f"export{EXTENSIONS[fmt]}"}

    exporter = EXPORTERS[fmt]
    content = exporter(papers)

    return {
        "format": fmt,
        "count": len(papers),
        "content": content,
        "filename": f"export{EXTENSIONS[fmt]}",
    }
