"""
共享工具函数。

包含搜索类型解析、排序类型解析、弹窗处理等模块间复用的逻辑。
"""

import asyncio

from playwright.async_api import Page

from cnki_mcp.config import (
    POPUP_SELECTORS,
    SEARCH_TYPE_ALIASES,
    SEARCH_TYPES,
    SORT_TYPE_ALIASES,
    SORT_TYPES,
)


def resolve_search_type(search_type: str) -> str:
    """解析搜索类型，支持中文或英文别名"""
    if not search_type:
        return "主题"
    search_type_lower = search_type.lower().strip()
    if search_type_lower in SEARCH_TYPE_ALIASES:
        return SEARCH_TYPE_ALIASES[search_type_lower]
    if search_type in SEARCH_TYPES:
        return search_type
    return "主题"


def resolve_sort_type(sort_type: str) -> str:
    """解析排序类型，支持中文或英文别名"""
    if not sort_type:
        return "相关度"
    sort_type_lower = sort_type.lower().strip()
    if sort_type_lower in SORT_TYPE_ALIASES:
        return SORT_TYPE_ALIASES[sort_type_lower]
    if sort_type in SORT_TYPES:
        return sort_type
    return "相关度"


async def dismiss_popups(page: Page) -> bool:
    """尝试关闭 CNKI 弹窗/遮罩"""
    for selector, kind in POPUP_SELECTORS:
        try:
            if kind == "css":
                elem = page.locator(selector).first
            else:
                elem = page.locator(f"xpath={selector}").first

            if await elem.count() > 0 and await elem.is_visible():
                await elem.click()
                await asyncio.sleep(0.5)
                return True
        except Exception:
            continue
    return False
