"""测试 config 模块中的搜索/排序类型映射。
"""

from cnki_mcp.config import (
    SEARCH_TYPES,
    SEARCH_TYPE_ALIASES,
    SORT_TYPES,
    SORT_TYPE_ALIASES,
)


def test_search_types_not_empty():
    assert len(SEARCH_TYPES) > 10
    assert "主题" in SEARCH_TYPES
    assert "作者" in SEARCH_TYPES


def test_search_type_aliases_mapping():
    assert SEARCH_TYPE_ALIASES["subject"] == "主题"
    assert SEARCH_TYPE_ALIASES["keyword"] == "关键词"
    assert SEARCH_TYPE_ALIASES["author"] == "作者"
    assert SEARCH_TYPE_ALIASES["title"] == "篇名"


def test_sort_types_not_empty():
    assert len(SORT_TYPES) >= 5
    assert "相关度" in SORT_TYPES
    assert "被引" in SORT_TYPES


def test_sort_type_aliases_mapping():
    assert SORT_TYPE_ALIASES["relevance"] == "相关度"
    assert SORT_TYPE_ALIASES["cited"] == "被引"
    assert SORT_TYPE_ALIASES["date"] == "发表时间"
