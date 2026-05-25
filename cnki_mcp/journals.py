"""
CNKI 期刊浏览工具。

支持三种操作：
- list_categories: 列出学科分类
- search_journals: 按关键词搜索期刊
- recent_articles: 获取期刊最新文章

需要浏览器。
"""

import asyncio
import random
from typing import Any

from playwright.async_api import Page

from cnki_mcp.utils import dismiss_popups


async def list_categories_impl(page: Page) -> dict[str, Any]:
    """列出 CNKI 期刊导航的学科分类"""
    await page.goto("https://navi.cnki.net/knavi/", wait_until="domcontentloaded", timeout=30_000)
    await asyncio.sleep(random.uniform(1, 2))
    await dismiss_popups(page)

    categories: list[dict[str, str]] = []

    try:
        # CNKI 期刊导航左侧的学科分类列表
        cat_els = await page.locator(".subject-list a, .catalog-list a, .left-nav a").all()
        for el in cat_els:
            text = (await el.text_content() or "").strip()
            href = (await el.get_attribute("href")) or ""
            if text and len(text) > 1:
                categories.append({"name": text, "url": href})
    except Exception:
        pass

    # Fallback: 尝试从主内容区域提取
    if not categories:
        try:
            links = await page.locator("a").all()
            seen = set()
            for link in links:
                text = (await link.text_content() or "").strip()
                href = (await link.get_attribute("href")) or ""
                if text and len(text) >= 2 and len(text) <= 20 and text not in seen:
                    if "knavi" in href or "journal" in href.lower():
                        categories.append({"name": text, "url": href})
                        seen.add(text)
        except Exception:
            pass

    return {
        "action": "list_categories",
        "categories": [c["name"] for c in categories],
        "details": categories,
        "total": len(categories),
    }


async def search_journals_impl(page: Page, keyword: str) -> dict[str, Any]:
    """按关键词搜索期刊"""
    await page.goto("https://navi.cnki.net/knavi/", wait_until="domcontentloaded", timeout=30_000)
    await asyncio.sleep(random.uniform(1, 2))
    await dismiss_popups(page)

    journals: list[dict[str, str]] = []

    # 在期刊导航页搜索
    try:
        search_input = page.locator('input[type="text"], input[placeholder*="搜索"], input[placeholder*="期刊"]').first
        if await search_input.count() > 0 and await search_input.is_visible():
            await search_input.fill(keyword)
            await asyncio.sleep(random.uniform(0.5, 1))

            # 找搜索按钮
            search_btn = page.locator('input[type="submit"], button[type="submit"], .search-btn, button:has-text("搜索")').first
            if await search_btn.count() > 0:
                await search_btn.click()
            else:
                await search_input.press("Enter")

            await asyncio.sleep(random.uniform(2, 3))

            # 解析搜索结果
            rows = page.locator("table tr, .journal-item, .journal-list li, .result-item")
            count = await rows.count()
            for i in range(min(count, 30)):
                row = rows.nth(i)
                text = (await row.text_content() or "").strip()
                if text and keyword[:2] in text:
                    link = row.locator("a").first
                    href = (await link.get_attribute("href")) or "" if await link.count() > 0 else ""
                    name = (await link.text_content() or "").strip() if await link.count() > 0 else text[:50]
                    if name and len(name) > 1:
                        journals.append({"name": name, "url": href, "info": text[:100]})
    except Exception:
        pass

    return {
        "action": "search_journals",
        "keyword": keyword,
        "journals": journals,
        "total": len(journals),
    }


async def recent_articles_impl(page: Page, journal_id: str, max_articles: int = 10) -> dict[str, Any]:
    """获取期刊的最新文章"""
    # journal_id 可以是期刊的 pykm 参数，也可以是完整 URL
    if journal_id.startswith("http"):
        url = journal_id
    else:
        url = f"https://navi.cnki.net/knavi/JournalDetail?pcode=CJFD&pykm={journal_id}"

    await page.goto("https://www.cnki.net/", wait_until="domcontentloaded", timeout=30_000)
    await asyncio.sleep(random.uniform(0.5, 1))

    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    await asyncio.sleep(random.uniform(2, 3))

    journal_name = ""
    articles: list[dict[str, str]] = []

    try:
        # 期刊名
        name_loc = page.locator("h1, .journal-title, .journal-name").first
        if await name_loc.count() > 0:
            journal_name = (await name_loc.text_content() or "").strip()
    except Exception:
        pass

    try:
        # 文章列表
        article_rows = page.locator("table tr, .article-item, .issue-item li, .paper-list li")
        count = await article_rows.count()
        for i in range(min(count, max_articles)):
            row = article_rows.nth(i)
            link = row.locator("a").first
            if await link.count() > 0:
                title = (await link.text_content() or "").strip()
                href = (await link.get_attribute("href")) or ""
                if title and len(title) > 5:
                    articles.append({"title": title, "url": href})
    except Exception:
        pass

    return {
        "action": "recent_articles",
        "journal_id": journal_id,
        "journal_name": journal_name,
        "articles": articles,
        "total": len(articles),
    }
