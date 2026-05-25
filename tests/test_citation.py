"""测试 citation 模块的引文格式化"""

import pytest

from cnki_mcp.citation import (
    format_citation_impl,
    SUPPORTED_STYLES,
    format_gbt7714,
    format_apa,
    format_mla,
    format_chicago,
    format_vancouver,
)
from cnki_mcp.exceptions import CitationError


def test_gbt7714_basic():
    result = format_gbt7714(
        title="人工智能在医学影像中的应用",
        authors=["张三", "李四", "王五"],
        source="中国医学杂志",
        year="2025",
        volume="46",
        issue="3",
        pages="1-15",
        doi="10.1234/test",
    )
    assert "人工智能在医学影像中的应用" in result
    assert "中国医学杂志" in result
    assert "2025" in result
    assert "46" in result
    assert "DOI" in result
    assert result.endswith(".")


def test_apa_basic():
    result = format_apa(
        title="Deep Learning in Medical Imaging",
        authors=["Smith, John", "Doe, Jane"],
        source="Journal of Medicine",
        year="2025",
        volume="46",
        issue="3",
        pages="1-15",
        doi="10.1234/test",
    )
    assert "2025" in result
    assert "Journal of Medicine" in result
    assert "10.1234/test" in result


def test_mla_basic():
    result = format_mla(
        title="AI in Healthcare",
        authors=["Smith, John", "Doe, Jane"],
        source="Medical Journal",
        year="2025",
    )
    assert "AI in Healthcare" in result
    assert "Medical Journal" in result
    assert "2025" in result


def test_chicago_basic():
    result = format_chicago(
        title="Machine Learning in Radiology",
        authors=["Smith, John"],
        source="Radiology Journal",
        year="2025",
        volume="46",
        pages="100-120",
    )
    assert "Machine Learning in Radiology" in result
    assert "Radiology Journal" in result


def test_vancouver_basic():
    result = format_vancouver(
        title="Clinical AI Applications",
        authors=["Smith, John", "Doe, Jane", "Lee, Kim"],
        source="The Lancet",
        year="2025",
        volume="400",
        issue="1",
        pages="50-60",
    )
    assert "Clinical AI Applications" in result
    assert "The Lancet" in result
    assert "2025" in result


def test_format_citation_impl_all_styles():
    for style in SUPPORTED_STYLES:
        result = format_citation_impl(
            title="测试论文",
            authors="张三,李四",
            source="测试期刊",
            year="2025",
            style=style,
        )
        assert result["style"] == style
        assert len(result["citation"]) > 0
        assert "测试论文" in result["citation"]


def test_format_citation_invalid_style():
    with pytest.raises(CitationError):
        format_citation_impl(
            title="test",
            authors="Smith",
            source="Journal",
            year="2025",
            style="invalid_style",
        )


def test_format_citation_empty_authors():
    with pytest.raises(CitationError):
        format_citation_impl(
            title="test",
            authors="",
            source="Journal",
            year="2025",
            style="gbt7714",
        )
