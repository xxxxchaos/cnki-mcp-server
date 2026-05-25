"""
CNKI MCP 服务器 — FastMCP 应用与工具注册。

提供 3 个 MCP 工具：
- search_cnki: 搜索 CNKI 论文
- get_paper_detail: 获取论文详情
- find_best_match: 快速标题匹配

使用方法:
    python -m cnki_mcp          # stdio 模式（Claude Code/Cursor）
    uvx cnki-mcp                # 一键运行
"""

import json
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from pydantic import Field

from cnki_mcp.browser import AsyncBrowserPool
from cnki_mcp.citation import format_citation_impl, SUPPORTED_STYLES
from cnki_mcp.config import SEARCH_TYPES, SEARCH_TYPE_ALIASES, SORT_TYPES
from cnki_mcp.detail import get_paper_detail_impl
from cnki_mcp.exceptions import CNKIError, CitationError, ExportError, ValidationError
from cnki_mcp.export import export_papers_impl, SUPPORTED_FORMATS
from cnki_mcp.journals import list_categories_impl, search_journals_impl, recent_articles_impl
from cnki_mcp.match import find_best_match_impl
from cnki_mcp.search import search_cnki_impl


@dataclass
class AppContext:
    """应用上下文 — 持有共享的浏览器池"""
    browser_pool: AsyncBrowserPool


@asynccontextmanager
async def lifespan(server: FastMCP):
    """MCP 服务器生命周期管理"""
    pool = AsyncBrowserPool()
    try:
        yield AppContext(browser_pool=pool)
    finally:
        await pool.close()


mcp = FastMCP(
    "CNKI 论文检索服务",
    lifespan=lifespan,
    instructions="""
CNKI (中国知网) 论文检索 MCP 服务器。

## 可用工具

### search_cnki
搜索 CNKI 论文，返回论文列表。
- query: 搜索关键词（必填）
- search_type: 搜索类型（可选，默认"主题"）
  - 支持: 主题、关键词、作者、篇名、作者单位、全文、DOI 等
  - 英文别名: subject, keyword, author, title, affiliation, fulltext, doi
- pages: 搜索页数（可选，默认1页，每页约20条）
- sort: 排序方式（可选，默认"相关度"）
  - 支持: 相关度、发表时间、被引、下载、综合
  - 英文别名: relevance, date, cited, download, composite

### get_paper_detail
获取论文详情页的完整信息。
- url: CNKI 论文详情页 URL（必填）

### find_best_match
快速查找与输入标题最匹配的论文。
- query: 论文标题（必填）

## 可用资源

### cnki://search-types
返回支持的搜索类型列表。

### cnki://status
返回服务器状态信息。

## 使用建议
1. 先用 search_cnki 搜索论文列表
2. 从结果中选择目标论文的 URL
3. 用 get_paper_detail 获取完整详情
4. 使用 sort="被引" 查找高被引论文
5. 使用 sort="发表时间" 查找最新论文

## 注意事项
- 每次搜索建议 1-3 页，避免过多请求
- 搜索间隔建议 2-3 秒，避免触发反爬
- 浏览器实例会在首次调用时启动，后续复用（更快）
"""
)


def _get_pool(ctx: Context = CurrentContext()) -> AsyncBrowserPool:
    """依赖注入：获取浏览器池"""
    return ctx.request_context.lifespan_context.browser_pool


# ==================== MCP 工具 ====================


@mcp.tool()
async def search_cnki(
    query: Annotated[str, Field(description="搜索关键词（必填）", min_length=1)],
    ctx: Context,
    search_type: Annotated[str, Field(
        description="搜索类型: 主题、关键词、作者、篇名、作者单位、全文、DOI、基金、摘要"
    )] = "主题",
    pages: Annotated[int, Field(
        description="搜索页数（每页约20条结果）",
        ge=1,
        le=10,
    )] = 1,
    sort: Annotated[str, Field(
        description="排序方式: 相关度、发表时间、被引、下载、综合 (英文: relevance, date, cited, download, composite)"
    )] = "相关度",
) -> dict:
    """
    搜索 CNKI 论文，返回论文列表。

    Args:
        query: 搜索关键词
        ctx: MCP 上下文（自动注入）
        search_type: 搜索类型，支持中英文
        pages: 搜索页数（1-10），每页约20条结果
        sort: 排序方式

    Returns:
        包含论文列表的字典
    """
    await ctx.info(f"开始搜索 CNKI: query='{query}', type='{search_type}', sort='{sort}', pages={pages}")
    await ctx.report_progress(progress=0, total=100)

    pool = _get_pool(ctx)
    page = await pool.new_page()
    try:
        result = await search_cnki_impl(page, query, search_type, pages, sort)
    except CNKIError as e:
        result = {"isError": True, "error": str(e), "error_type": type(e).__name__, "papers": []}
        await ctx.error(f"搜索失败: {e}")
    except Exception as e:
        result = {"isError": True, "error": str(e), "error_type": "SearchError", "papers": []}
        await ctx.error(f"搜索异常: {e}")
    finally:
        await page.close()

    await ctx.report_progress(progress=100, total=100)
    if not result.get("isError"):
        await ctx.info(f"搜索完成，找到 {result.get('total_papers', 0)} 篇论文")
    return result


@mcp.tool()
async def get_paper_detail(
    url: Annotated[str, Field(description="CNKI 论文详情页 URL（通常从 search_cnki 结果中获取）")],
    ctx: Context,
) -> dict:
    """
    获取 CNKI 论文详情页的完整信息。

    Args:
        url: CNKI 论文详情页 URL
        ctx: MCP 上下文（自动注入）

    Returns:
        包含论文完整信息的字典
    """
    if not url or not url.strip():
        return {"isError": True, "error": "URL 不能为空", "error_type": "ValidationError"}
    if "cnki" not in url.lower():
        return {"isError": True, "error": "URL 必须是 CNKI 链接", "error_type": "ValidationError"}

    await ctx.info(f"获取论文详情: {url[:80]}...")
    await ctx.report_progress(progress=0, total=100)

    pool = _get_pool(ctx)
    page = await pool.new_page()
    try:
        result = await get_paper_detail_impl(page, url)
    except CNKIError as e:
        result = {"isError": True, "error": str(e), "error_type": type(e).__name__, "url": url}
        await ctx.error(f"获取详情失败: {e}")
    except Exception as e:
        result = {"isError": True, "error": str(e), "error_type": "DetailError", "url": url}
        await ctx.error(f"获取详情异常: {e}")
    finally:
        await page.close()

    await ctx.report_progress(progress=100, total=100)
    if not result.get("isError"):
        await ctx.info(f"获取详情成功: {result.get('title', '')[:50]}")
    return result


@mcp.tool()
async def find_best_match(
    query: Annotated[str, Field(description="论文标题或关键词", min_length=1)],
    ctx: Context,
) -> dict:
    """
    快速查找与输入标题最匹配的 CNKI 论文。

    使用字符匹配算法，适合用于验证论文标题或快速定位特定论文。

    Args:
        query: 论文标题或关键词
        ctx: MCP 上下文（自动注入）

    Returns:
        最匹配论文的标题和 URL
    """
    await ctx.info(f"查找最佳匹配: '{query[:50]}'")
    await ctx.report_progress(progress=0, total=100)

    pool = _get_pool(ctx)
    page = await pool.new_page()
    try:
        result = await find_best_match_impl(page, query)
    except CNKIError as e:
        result = {"isError": True, "error": str(e), "error_type": type(e).__name__}
        await ctx.error(f"匹配失败: {e}")
    except Exception as e:
        result = {"isError": True, "error": str(e), "error_type": "MatchError"}
        await ctx.error(f"匹配异常: {e}")
    finally:
        await page.close()

    await ctx.report_progress(progress=100, total=100)
    if not result.get("isError"):
        match = result.get("best_match")
        if match:
            await ctx.info(f"找到最佳匹配: {match['title'][:50]}")
        else:
            await ctx.info("未找到匹配结果")
    return result


@mcp.tool()
async def format_citation(
    ctx: Context,
    title: Annotated[str, Field(description="论文标题")],
    authors: Annotated[str, Field(description="作者列表，逗号分隔（如：张三,李四,王五）")],
    source: Annotated[str, Field(description="期刊/来源名称")],
    year: Annotated[str, Field(description="发表年份")],
    volume: Annotated[str, Field(description="卷号")] = "",
    issue: Annotated[str, Field(description="期号")] = "",
    pages: Annotated[str, Field(description="起止页码（如：1-15）")] = "",
    doi: Annotated[str, Field(description="DOI")] = "",
    style: Annotated[str, Field(
        description=f"引文风格: gbt7714, apa, mla, chicago, vancouver"
    )] = "gbt7714",
) -> dict:
    """
    生成格式化引文。

    支持 GB/T 7714-2015、APA 7th、MLA 9th、Chicago、Vancouver 五种风格。
    适合在论文写作中快速生成参考文献引用。

    Args:
        title: 论文标题
        authors: 作者列表（逗号分隔）
        source: 期刊名称
        year: 发表年份
        volume: 卷号
        issue: 期号
        pages: 页码
        doi: DOI
        style: 引文风格

    Returns:
        包含格式化引文的字典
    """
    await ctx.info(f"生成引文: style={style}, title={title[:50]}...")
    try:
        result = format_citation_impl(
            title=title, authors=authors, source=source, year=year,
            volume=volume, issue=issue, pages=pages, doi=doi, style=style,
        )
        await ctx.info(f"引文生成完成 ({style})")
        return result
    except CitationError as e:
        return {"isError": True, "error": str(e), "error_type": "CitationError"}
    except Exception as e:
        return {"isError": True, "error": str(e), "error_type": "CitationError"}


@mcp.tool()
async def browse_journals(
    ctx: Context,
    action: Annotated[str, Field(
        description="操作类型: list_categories（列出学科分类）, search_journals（搜索期刊）, recent_articles（期刊最新文章）"
    )] = "list_categories",
    keyword: Annotated[str, Field(description="期刊关键词（action=search_journals 时使用）")] = "",
    journal_id: Annotated[str, Field(description="期刊 ID 或 URL（action=recent_articles 时使用）")] = "",
    max_articles: Annotated[int, Field(description="获取文章数上限", ge=1, le=50)] = 10,
) -> dict:
    """
    浏览 CNKI 期刊导航。

    支持三种操作：
    - list_categories: 列出 CNKI 的学科分类
    - search_journals: 按关键词搜索期刊
    - recent_articles: 查看某个期刊的最新发表文章

    Args:
        action: 操作类型
        keyword: 期刊关键词（action=search_journals 时必填）
        journal_id: 期刊 ID 或完整 URL（action=recent_articles 时必填）
        max_articles: 获取文章数上限

    Returns:
        对应操作的返回结果
    """
    await ctx.info(f"期刊浏览: action={action}")

    if action == "search_journals" and not keyword:
        return {"isError": True, "error": "搜索期刊需要提供 keyword 参数", "error_type": "ValidationError"}
    if action == "recent_articles" and not journal_id:
        return {"isError": True, "error": "获取文章需要提供 journal_id 参数", "error_type": "ValidationError"}

    pool = _get_pool(ctx)
    page = await pool.new_page()
    try:
        if action == "list_categories":
            result = await list_categories_impl(page)
        elif action == "search_journals":
            result = await search_journals_impl(page, keyword)
        elif action == "recent_articles":
            result = await recent_articles_impl(page, journal_id, max_articles)
        else:
            result = {"isError": True, "error": f"不支持的操作: {action}", "error_type": "ValidationError"}
    except CNKIError as e:
        result = {"isError": True, "error": str(e), "error_type": type(e).__name__}
        await ctx.error(f"期刊浏览失败: {e}")
    except Exception as e:
        result = {"isError": True, "error": str(e), "error_type": "JournalError"}
        await ctx.error(f"期刊浏览异常: {e}")
    finally:
        await page.close()

    await ctx.info(f"期刊浏览完成: {result.get('total', 0)} 条结果")
    return result


@mcp.tool()
async def export_papers(
    ctx: Context,
    papers: Annotated[str, Field(description="论文列表 JSON 字符串（通常从 search_cnki 结果中提取 papers 数组）")],
    format: Annotated[str, Field(
        description="导出格式: csv, json, bibtex, ris"
    )] = "json",
) -> dict:
    """
    批量导出论文为指定格式。

    支持 CSV、JSON、BibTeX、RIS 四种格式。
    适合将搜索结果保存为文献管理软件兼容的文件。

    Args:
        papers: 论文列表 JSON 字符串
        format: 导出格式

    Returns:
        包含导出内容和文件名的字典
    """
    await ctx.info(f"导出论文: format={format}")
    try:
        result = export_papers_impl(papers, format)
        await ctx.info(f"导出完成: {result.get('count', 0)} 篇 ({format})")
        return result
    except ExportError as e:
        return {"isError": True, "error": str(e), "error_type": "ExportError"}
    except Exception as e:
        return {"isError": True, "error": str(e), "error_type": "ExportError"}


# ==================== MCP 资源 ====================


@mcp.resource("cnki://search-types")
async def get_search_types(ctx: Context) -> str:
    """返回支持的搜索类型列表"""
    return json.dumps({
        "description": "CNKI 支持的搜索类型",
        "chinese_types": list(SEARCH_TYPES.keys()),
        "english_aliases": list(SEARCH_TYPE_ALIASES.keys()),
        "default": "主题",
    }, ensure_ascii=False, indent=2)


@mcp.resource("cnki://status")
async def get_server_status(ctx: Context) -> str:
    """返回服务器状态信息"""
    return json.dumps({
        "server_name": "CNKI 论文检索服务",
        "version": "0.2.0",
        "engine": "Playwright",
        "features": [
            "浏览器池复用",
            "空闲超时自动关闭（10分钟）",
            "async/await 原生异步",
            "独立 Page 会话隔离",
            "反检测脚本注入",
            "Playwright 自动等待",
        ],
        "tools": [
            "search_cnki", "get_paper_detail", "find_best_match",
            "format_citation", "browse_journals", "export_papers",
        ],
        "resources": [
            "cnki://search-types", "cnki://citation-styles",
            "cnki://export-formats", "cnki://status",
        ],
    }, ensure_ascii=False, indent=2)


@mcp.resource("cnki://citation-styles")
async def get_citation_styles(ctx: Context) -> str:
    """返回支持的引文格式列表"""
    return json.dumps({
        "description": "支持的引文格式",
        "styles": {
            "gbt7714": "GB/T 7714-2015 中国国家标准（中文论文推荐）",
            "apa": "APA 7th Edition 美国心理学会",
            "mla": "MLA 9th Edition 现代语言学会",
            "chicago": "Chicago Notes & Bibliography",
            "vancouver": "Vancouver/ICMJE 生物医学通用格式",
        },
        "default": "gbt7714",
    }, ensure_ascii=False, indent=2)


@mcp.resource("cnki://export-formats")
async def get_export_formats(ctx: Context) -> str:
    """返回支持的导出格式列表"""
    return json.dumps({
        "description": "支持的导出格式",
        "formats": {
            "json": "格式化 JSON，适合编程处理",
            "csv": "CSV 表格，适合 Excel 打开",
            "bibtex": "BibTeX 格式，适合 LaTeX/Zotero",
            "ris": "RIS 格式，适合 EndNote/Mendeley/Zotero",
        },
        "default": "json",
    }, ensure_ascii=False, indent=2)


# ==================== 入口 ====================


def main() -> None:
    """CLI 入口"""
    mcp.run()
