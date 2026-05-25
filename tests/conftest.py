"""pytest 配置与 fixtures"""

import pytest


@pytest.fixture
def sample_paper() -> dict:
    """标准测试论文数据"""
    return {
        "title": "深度学习在医学图像分析中的应用",
        "url": "https://kns.cnki.net/kcms2/article/abstract?v=test",
        "authors": ["张三", "李四"],
        "source": "中国医学杂志",
        "date": "2025-05-01",
        "cited_count": "10",
        "download_count": "50",
    }
