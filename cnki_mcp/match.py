"""
CNKI 论文标题快速匹配。

使用字符匹配算法，适合验证论文标题或快速定位特定论文。
"""

import asyncio
import random
from typing import Any

from playwright.async_api import Page

from cnki_mcp.search import dismiss_popups, human_type, submit_search
from cnki_mcp.config import SELECTOR_SEARCH_INPUT, SELECTOR_TITLE_LINK


def find_closest_title(query: str, titles: list[str]) -> int:
    """根据字符匹配度选择最接近的搜索结果"""
    max_similar = 0
    best_index = 0
    for i, title in enumerate(titles):
        common_chars = sum(c in title for c in query)
        if common_chars > max_similar:
            max_similar = common_chars
            best_index = i
    return best_index


async def find_best_match_impl(page: Page, query: str) -> dict[str, Any]:
    """搜索并返回最匹配论文的标题和 URL"""
    await page.goto("https://www.cnki.net/", wait_until="domcontentloaded")
    await asyncio.sleep(random.uniform(1, 2))
    await dismiss_popups(page)

    search_box = page.locator(SELECTOR_SEARCH_INPUT)
    await search_box.wait_for(timeout=15_000)
    await human_type(page, SELECTOR_SEARCH_INPUT, query)
    await submit_search(page)
    await asyncio.sleep(random.uniform(2, 3))

    result_titles: list[str] = []
    result_urls: list[str] = []

    try:
        await page.wait_for_selector(SELECTOR_TITLE_LINK, timeout=15_000)
        links = page.locator(SELECTOR_TITLE_LINK)
        count = await links.count()
        for i in range(count):
            link = links.nth(i)
            text = (await link.text_content() or "").strip()
            href = (await link.get_attribute("href")) or ""
            if text:
                result_titles.append(text)
                result_urls.append(href)
    except Exception:
        pass

    if not result_titles:
        return {"query": query, "best_match": None, "message": "未找到结果"}

    idx = find_closest_title(query, result_titles)
    return {
        "query": query,
        "best_match": {
            "title": result_titles[idx],
            "url": result_urls[idx],
        },
        "total_results": len(result_titles),
    }
