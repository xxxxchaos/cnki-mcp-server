"""测试 export 模块的批量导出"""

import json

import pytest

from cnki_mcp.export import (
    export_papers_impl,
    export_json,
    export_csv,
    export_bibtex,
    export_ris,
    SUPPORTED_FORMATS,
)
from cnki_mcp.exceptions import ExportError


SAMPLE_PAPERS = [
    {
        "title": "深度学习在医学影像中的应用",
        "authors": ["张三", "李四"],
        "source": "中国医学杂志",
        "date": "2025-01-01",
        "year": "2025",
        "volume": "46",
        "issue": "3",
        "pages": "1-15",
        "doi": "10.1234/test.001",
        "cited_count": "10",
        "download_count": "50",
    },
    {
        "title": "人工智能辅助临床诊断研究",
        "authors": ["王五", "赵六"],
        "source": "中华医学杂志",
        "date": "2025-02-01",
        "year": "2025",
        "volume": "45",
        "issue": "2",
        "pages": "20-30",
        "doi": "10.1234/test.002",
        "cited_count": "5",
        "download_count": "30",
    },
]


def test_export_json():
    content = export_json(SAMPLE_PAPERS)
    data = json.loads(content)
    assert len(data) == 2
    assert data[0]["title"] == "深度学习在医学影像中的应用"


def test_export_csv():
    content = export_csv(SAMPLE_PAPERS)
    lines = content.strip().split("\n")
    assert len(lines) == 3  # header + 2 rows
    assert "title" in lines[0]
    assert "深度学习" in lines[1]


def test_export_bibtex():
    content = export_bibtex(SAMPLE_PAPERS)
    assert "@article{" in content
    assert "深度学习在医学影像中的应用" in content
    assert content.count("@article{") == 2


def test_export_ris():
    content = export_ris(SAMPLE_PAPERS)
    assert "TY  - JOUR" in content
    assert "ER  - " in content
    assert content.count("TY  - JOUR") == 2


def test_export_papers_impl_json():
    papers_json = json.dumps(SAMPLE_PAPERS)
    result = export_papers_impl(papers_json, "json")
    assert result["format"] == "json"
    assert result["count"] == 2
    assert result["filename"] == "export.json"
    assert len(result["content"]) > 0


def test_export_papers_impl_bibtex():
    papers_json = json.dumps(SAMPLE_PAPERS)
    result = export_papers_impl(papers_json, "bibtex")
    assert result["format"] == "bibtex"
    assert result["count"] == 2
    assert result["filename"] == "export.bib"


def test_export_papers_impl_all_formats():
    papers_json = json.dumps(SAMPLE_PAPERS)
    for fmt in SUPPORTED_FORMATS:
        result = export_papers_impl(papers_json, fmt)
        assert result["count"] == 2
        assert len(result["content"]) > 0


def test_export_papers_invalid_format():
    with pytest.raises(ExportError):
        export_papers_impl("[]", "invalid")


def test_export_papers_invalid_json():
    with pytest.raises(ExportError):
        export_papers_impl("not valid json", "json")


def test_export_papers_empty():
    result = export_papers_impl("[]", "json")
    assert result["count"] == 0
    assert result["content"] == ""
