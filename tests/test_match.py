"""测试 match 模块的字符匹配算法"""

from cnki_mcp.match import find_closest_title


def test_exact_match():
    titles = ["深度学习在NLP中的应用", "机器学习基础"]
    assert find_closest_title("深度学习在NLP中的应用", titles) == 0


def test_partial_match():
    titles = ["基于深度学习的图像识别研究", "机器学习在医疗中的应用"]
    assert find_closest_title("深度学习图像识别", titles) == 0


def test_single_result():
    titles = ["唯一论文"]
    assert find_closest_title("任何标题", titles) == 0


def test_empty_titles():
    titles: list[str] = []
    # 空列表不会被调用（调用方会先检查）
    assert find_closest_title("test", titles) == 0
