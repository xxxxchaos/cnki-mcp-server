"""
CNKI 引文格式化工具。

支持 5 种引文风格：
- gbt7714: GB/T 7714-2015（中国国家标准）
- apa: APA 7th Edition
- mla: MLA 9th Edition
- chicago: Chicago Notes & Bibliography
- vancouver: Vancouver/ICMJE

纯逻辑模块，不需要浏览器。
"""

from cnki_mcp.exceptions import CitationError

SUPPORTED_STYLES = ["gbt7714", "apa", "mla", "chicago", "vancouver"]


def _format_authors_gbt7714(authors: list[str]) -> str:
    """GB/T 7714 作者格式：作者1,作者2,作者3,等"""
    if not authors:
        return ""
    names = [a.split("(")[0].strip() for a in authors]  # 去除机构后缀
    names = [n for n in names if n]
    if len(names) <= 3:
        return ",".join(names)
    return ",".join(names[:3]) + ",等"


def _format_authors_apa(authors: list[str]) -> str:
    """APA 7 作者格式：LastName, F. M., & LastName, F. M."""
    if not authors:
        return ""
    names = [a.split("(")[0].strip() for a in authors]
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} & {names[1]}"
    if len(names) <= 20:
        return ", ".join(names[:-1]) + f", & {names[-1]}"
    return ", ".join(names[:19]) + f", ... {names[-1]}"


def _format_authors_mla(authors: list[str]) -> str:
    """MLA 9 作者格式：LastName, FirstName, and FirstName LastName"""
    if not authors:
        return ""
    names = [a.split("(")[0].strip() for a in authors]
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return f"{names[0]}, et al."


def _format_authors_chicago(authors: list[str]) -> str:
    """Chicago 作者格式：LastName, FirstName, and FirstName LastName"""
    return _format_authors_mla(authors)


def _format_authors_vancouver(authors: list[str]) -> str:
    """Vancouver 作者格式：LastName AB, LastName CD"""
    if not authors:
        return ""
    names = [a.split("(")[0].strip() for a in authors]
    names = [n for n in names if n]
    if not names:
        return ""
    if len(names) <= 6:
        return ", ".join(names)
    return ", ".join(names[:6]) + ", et al."


def format_gbt7714(
    title: str,
    authors: list[str],
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    """GB/T 7714-2015 期刊论文格式"""
    author_str = _format_authors_gbt7714(authors)
    citation = f"{author_str}. {title}[J]. {source}"
    if year:
        citation += f", {year}"
    if volume:
        citation += f", {volume}"
        if issue:
            citation += f"({issue})"
    if pages:
        citation += f": {pages}"
    citation += "."
    if doi:
        citation += f" DOI:{doi}."
    return citation


def format_apa(
    title: str,
    authors: list[str],
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    """APA 7th Edition 期刊论文格式"""
    author_str = _format_authors_apa(authors)
    citation = f"{author_str} ({year}). {title}. *{source}*"
    if volume:
        citation += f", *{volume}*"
        if issue:
            citation += f"({issue})"
    if pages:
        citation += f", {pages}"
    citation += "."
    if doi:
        citation += f" https://doi.org/{doi}"
    return citation


def format_mla(
    title: str,
    authors: list[str],
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    """MLA 9th Edition 期刊论文格式"""
    author_str = _format_authors_mla(authors)
    citation = f'{author_str}. "{title}." *{source}*'
    if volume:
        citation += f", vol. {volume}"
    if issue:
        citation += f", no. {issue}"
    if year:
        citation += f", {year}"
    if pages:
        citation += f", pp. {pages}"
    citation += "."
    if doi:
        citation += f" doi:{doi}."
    return citation


def format_chicago(
    title: str,
    authors: list[str],
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    """Chicago Notes & Bibliography 期刊论文格式"""
    author_str = _format_authors_chicago(authors)
    citation = f'{author_str}. "{title}." *{source}* {volume}'
    if issue:
        citation += f", no. {issue}"
    if year:
        citation += f" ({year})"
    if pages:
        citation += f": {pages}"
    citation += "."
    if doi:
        citation += f" https://doi.org/{doi}."
    return citation


def format_vancouver(
    title: str,
    authors: list[str],
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
) -> str:
    """Vancouver/ICMJE 期刊论文格式"""
    author_str = _format_authors_vancouver(authors)
    citation = f"{author_str}. {title}. {source}."
    if year:
        citation += f" {year}"
    if volume:
        citation += f";{volume}"
        if issue:
            citation += f"({issue})"
    if pages:
        citation += f":{pages}"
    citation += "."
    if doi:
        citation += f" doi:{doi}."
    return citation


FORMATTERS = {
    "gbt7714": format_gbt7714,
    "apa": format_apa,
    "mla": format_mla,
    "chicago": format_chicago,
    "vancouver": format_vancouver,
}


def format_citation_impl(
    title: str,
    authors: str,
    source: str,
    year: str,
    volume: str = "",
    issue: str = "",
    pages: str = "",
    doi: str = "",
    style: str = "gbt7714",
) -> dict:
    """引文格式化核心逻辑"""
    style = style.lower().strip()
    if style not in FORMATTERS:
        raise CitationError(
            f"不支持的引文风格: {style}。支持: {', '.join(SUPPORTED_STYLES)}"
        )

    author_list = [a.strip() for a in authors.split(",") if a.strip()]
    if not author_list:
        raise CitationError("作者列表不能为空")

    formatter = FORMATTERS[style]
    citation = formatter(
        title=title.strip(),
        authors=author_list,
        source=source.strip(),
        year=year.strip(),
        volume=volume.strip(),
        issue=issue.strip(),
        pages=pages.strip(),
        doi=doi.strip(),
    )

    return {
        "citation": citation,
        "style": style,
    }
