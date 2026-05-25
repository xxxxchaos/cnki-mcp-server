# CNKI MCP Server

[![PyPI version](https://img.shields.io/pypi/v/cnki-mcp-server.svg)](https://pypi.org/project/cnki-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CNKI (中国知网) MCP Server** — 通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 为 AI Agent 提供中文学术论文检索能力。

## 功能

| 工具 | 说明 | 需要浏览器 |
|------|------|-----------|
| `search_cnki` | 搜索 CNKI 论文，支持多页、多种搜索类型和排序 | 是 |
| `get_paper_detail` | 获取论文详情（标题、摘要、作者、关键词、DOI 等 17 字段） | 是 |
| `find_best_match` | 快速匹配论文标题，验证引用信息 | 是 |
| `format_citation` | 引文格式化（GB/T 7714, APA, MLA, Chicago, Vancouver） | 否 |
| `browse_journals` | 期刊浏览（学科分类、期刊搜索、最新文章） | 是 |
| `export_papers` | 批量导出（CSV, JSON, BibTeX, RIS） | 否 |

### 搜索类型

支持 15 种搜索类型：主题、关键词、篇名、作者、作者单位、全文、DOI、基金、摘要等（中英文别名均可）。

### 排序方式

相关度 / 发表时间 / 被引 / 下载 / 综合（支持英文别名：relevance, date, cited, download, composite）。

## 安装

```bash
pip install cnki-mcp-server
python -m playwright install chromium
```

> **注意**: Playwright Chromium 约 300MB，首次安装需要下载，后续无需重复安装。

## 使用

### Claude Code

在 `.claude/settings.json` 或 Claude Code 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "cnki": {
      "command": "python",
      "args": ["-m", "cnki_mcp"]
    }
  }
}
```

### 命令行直接使用

```bash
python -m cnki_mcp
```

## 要求

- Python >= 3.10
- Playwright Chromium（首次使用时自动安装）

## 引文格式

| 风格 | 标准 | 适用场景 |
|------|------|----------|
| `gbt7714` | GB/T 7714-2015 | 中文学位论文、中文期刊 |
| `apa` | APA 7th Edition | 心理学、教育学、社会科学 |
| `mla` | MLA 9th Edition | 语言文学、人文学科 |
| `chicago` | Chicago Notes & Bibliography | 历史学、艺术学 |
| `vancouver` | Vancouver/ICMJE | 生物医学、临床医学 |

## 导出格式

| 格式 | 适用软件 |
|------|----------|
| JSON | 编程处理、数据分析 |
| CSV | Excel、Google Sheets |
| BibTeX | LaTeX、Zotero、JabRef |
| RIS | EndNote、Mendeley、Zotero |

## 技术实现

- **引擎**: Playwright（自带签名 Chromium，消除 macOS codesign 问题，跨平台零配置）
- **MCP 框架**: FastMCP
- **并发**: 原生 async/await
- **反检测**: 随机 User-Agent、模拟人类输入、navigator.webdriver 覆写
- **会话复用**: 共享 BrowserContext，Cookie 互通，避免 CNKI 验证码

## 开发

```bash
git clone https://github.com/xxxxchaos/cnki-mcp-server.git
cd cnki-mcp-server
pip install -e ".[dev]"
python -m playwright install chromium
pytest tests/ -v
```

## 许可

MIT License
