"""测试 utils 模块的工具函数"""

from cnki_mcp.utils import resolve_search_type, resolve_sort_type


def test_resolve_search_type_chinese():
    assert resolve_search_type("主题") == "主题"
    assert resolve_search_type("关键词") == "关键词"
    assert resolve_search_type("作者") == "作者"


def test_resolve_search_type_english():
    assert resolve_search_type("subject") == "主题"
    assert resolve_search_type("keyword") == "关键词"
    assert resolve_search_type("author") == "作者"
    assert resolve_search_type("title") == "篇名"


def test_resolve_search_type_default():
    assert resolve_search_type("") == "主题"
    assert resolve_search_type("不存在的类型") == "主题"


def test_resolve_sort_type_chinese():
    assert resolve_sort_type("相关度") == "相关度"
    assert resolve_sort_type("被引") == "被引"
    assert resolve_sort_type("发表时间") == "发表时间"


def test_resolve_sort_type_english():
    assert resolve_sort_type("relevance") == "相关度"
    assert resolve_sort_type("cited") == "被引"
    assert resolve_sort_type("date") == "发表时间"


def test_resolve_sort_type_default():
    assert resolve_sort_type("") == "相关度"
    assert resolve_sort_type("不存在的排序") == "相关度"
