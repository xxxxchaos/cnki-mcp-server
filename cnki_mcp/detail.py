"""
CNKI 论文详情页解析。

从 Selenium 迁移到 Playwright，提取论文的全部元数据字段。
"""

import asyncio
import random
from typing import Any

from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

from cnki_mcp.exceptions import DetailError


async def get_paper_detail_impl(page: Page, url: str) -> dict[str, Any]:
    """获取论文详情页的全部信息"""
    paper: dict[str, Any] = {
        "url": url,
        "title": "",
        "title_en": "",
        "authors": [],
        "institutions": [],
        "abstract": "",
        "abstract_en": "",
        "keywords": [],
        "keywords_en": [],
        "source": "",
        "year": "",
        "volume": "",
        "issue": "",
        "pages": "",
        "doi": "",
        "cited_count": "",
        "download_count": "",
        "fund": "",
        "classification": "",
    }

    try:
        # 先访问 CNKI 首页建立会话（避免直接访问抽象页触发验证码）
        await page.goto("https://www.cnki.net/", wait_until="domcontentloaded", timeout=30_000)
        await asyncio.sleep(random.uniform(1, 2))
        # 检查是否被反爬拦截
        homepage_content = await page.content()
        if len(homepage_content) < 200:
            raise DetailError(
                "CNKI 返回了空页面，可能触发了反爬拦截（HTTP 418）。"
                "请检查网络环境，或尝试设置 CNKI_PROXY 环境变量更换代理 IP。"
            )

        await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        await asyncio.sleep(random.uniform(1.5, 2.5))
    except PlaywrightTimeout:
        raise DetailError(f"页面加载超时: {url[:80]}")
    except Exception as e:
        raise DetailError(f"页面导航失败: {e}") from e

    # 标题
    try:
        loc = page.locator(".wx-tit h1")
        if await loc.count() > 0:
            paper["title"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 英文标题
    try:
        loc = page.locator(".wx-tit h2")
        if await loc.count() > 0:
            paper["title_en"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 作者
    try:
        author_els = await page.locator("h3.author span a").all()
        paper["authors"] = [
            (await a.text_content() or "").strip()
            for a in author_els
        ]
    except Exception:
        pass

    # 机构
    try:
        org_els = await page.locator("h3.orgn span a").all()
        paper["institutions"] = [
            (await o.text_content() or "").strip()
            for o in org_els
        ]
    except Exception:
        pass

    # 摘要
    try:
        loc = page.locator("#ChDivSummary")
        if await loc.count() > 0:
            paper["abstract"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 英文摘要
    try:
        loc = page.locator("#EnChDivSummary")
        if await loc.count() > 0:
            paper["abstract_en"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 关键词
    try:
        kw_els = await page.locator("p.keywords a").all()
        keywords = []
        for k in kw_els:
            text = (await k.text_content() or "").strip().rstrip(";；")
            if text:
                keywords.append(text)
        paper["keywords"] = keywords
    except Exception:
        pass

    # 来源
    try:
        loc = page.locator('div.top-tip a[href*="navi.cnki.net"]')
        if await loc.count() > 0:
            paper["source"] = (await loc.first.text_content() or "").strip().rstrip(" .")
    except Exception:
        pass

    # 年/卷/期/页 — 遍历 top-tip 中所有 span 查找逗号分隔的出版信息
    try:
        spans = page.locator("div.top-tip span")
        cnt = await spans.count()
        for i in range(cnt):
            text = (await spans.nth(i).text_content() or "").strip()
            # 匹配 "2022, 45(3): 1-15" 这样的模式
            if "," in text and any(c.isdigit() for c in text):
                parts = text.split(",")
                paper["year"] = parts[0].strip()
                if len(parts) > 1:
                    rest = parts[1].strip()
                    if "(" in rest and ")" in rest:
                        paper["volume"] = rest.split("(")[0].strip()
                        paper["issue"] = rest.split("(")[1].split(")")[0].strip()
                    if ":" in rest:
                        paper["pages"] = rest.split(":")[-1].strip()
                break
    except Exception:
        pass

    # DOI — 在 li.top-space 中查找包含 "DOI" 的项
    try:
        lis = page.locator("li.top-space")
        cnt = await lis.count()
        for i in range(cnt):
            text = (await lis.nth(i).text_content() or "").strip()
            if "DOI" in text:
                # 提取 "DOI：10.xxx" 中的值
                doi_val = text.replace("DOI", "").replace("：", "").replace(":", "").strip()
                if doi_val:
                    paper["doi"] = doi_val
                break
    except Exception:
        pass

    # 被引次数
    try:
        loc = page.locator("span#refs a")
        if await loc.count() > 0:
            paper["cited_count"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 下载次数
    try:
        loc = page.locator("span#DownLoadParts a")
        if await loc.count() > 0:
            paper["download_count"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 基金
    try:
        loc = page.locator('li:has-text("基金") p')
        if await loc.count() == 0:
            loc = page.locator("p.funds span")
        if await loc.count() > 0:
            paper["fund"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    # 分类号
    try:
        loc = page.locator('li:has-text("分类号") p')
        if await loc.count() > 0:
            paper["classification"] = (await loc.first.text_content() or "").strip()
    except Exception:
        pass

    return paper
