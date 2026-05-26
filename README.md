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
>
> **新版 Ubuntu（26.04+）用户**: Playwright 尚未官方支持 Ubuntu 26.04，请设置环境变量后再安装 Chromium：
> ```bash
> PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64 python -m playwright install chromium
> ```
>
> **SOCKS 代理用户**: 如果系统配置了 SOCKS 代理（`ALL_PROXY=socks5://...`），请确保安装时包含 socks 支持：
> ```bash
> pip install cnki-mcp-server[socks]
> ```

## 代理配置

如果你的网络环境需要通过代理访问外网，请设置以下环境变量：

| 环境变量 | 说明 |
|----------|------|
| `CNKI_PROXY` | 代理地址（优先使用），如 `socks5://127.0.0.1:4781` 或 `http://127.0.0.1:4780` |
| `HTTPS_PROXY` / `https_proxy` | 标准 HTTPS 代理地址（`CNKI_PROXY` 未设置时使用） |
| `ALL_PROXY` / `all_proxy` | 全局代理地址（上述均未设置时使用） |
| `CNKI_PROXY_USERNAME` / `PROXY_USERNAME` | 代理用户名（需要认证时使用） |
| `CNKI_PROXY_PASSWORD` / `PROXY_PASSWORD` | 代理密码（需要认证时使用） |
| `NO_PROXY` / `no_proxy` | 不走代理的域名/地址列表，逗号分隔。如 `cnki.net,*.cnki.net` |

> **注意**:
> - Playwright 不支持 `socks5h://`（DNS 通过代理解析），会自动替换为 `socks5://`。
> - 如果使用 Clash 等代理工具，建议搭配 `NO_PROXY` 排除国内网站（如 `cnki.net`），让 CNKI 走直连避免 CDN 拦截（HTTP 418）。

### OpenCode 示例

```json
{
  "mcpServers": {
    "cnki": {
      "command": "python",
      "args": ["-m", "cnki_mcp"],
      "env": {
        "HTTPS_PROXY": "socks5://127.0.0.1:4781",
        "NO_PROXY": "cnki.net,*.cnki.net",
        "PLAYWRIGHT_HOST_PLATFORM_OVERRIDE": "ubuntu24.04-x64"
      }
    }
  }
}
```

### Claude Code 示例

```json
{
  "mcpServers": {
    "cnki": {
      "command": "python",
      "args": ["-m", "cnki_mcp"],
      "env": {
        "HTTPS_PROXY": "socks5://127.0.0.1:4781",
        "NO_PROXY": "cnki.net,*.cnki.net",
        "PLAYWRIGHT_HOST_PLATFORM_OVERRIDE": "ubuntu24.04-x64"
      }
    }
  }
}
```

## 使用

CNKI MCP Server 是一个标准 MCP 服务器，支持所有兼容 MCP（Model Context Protocol）的 AI Agent 平台。

### OpenCode

在 OpenCode 配置文件（`~/.config/opencode/config.json` 或项目 `.opencode.json`）中添加：

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

### Claude Code

在 `.claude/settings.json` 中添加：

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

### Claude Desktop

在 Claude Desktop 配置（`~/Library/Application Support/Claude/claude_desktop_config.json`）中添加：

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

### Cursor

在 Cursor 设置 → MCP 中添加新服务器，或编辑 `~/.cursor/mcp.json`：

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

### Windsurf

在 `~/.codeium/windsurf/mcp_config.json` 中添加：

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

### VS Code / Cline

在 Cline 扩展设置 → MCP Servers 中添加，或编辑 `~/AppData/Roaming/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`：

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

### VS Code / Continue

在 Continue 配置（`~/.continue/config.json`）中添加：

```json
{
  "experimental": {
    "mcpServers": {
      "cnki": {
        "command": "python",
        "args": ["-m", "cnki_mcp"]
      }
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

## 故障排查

### Playwright 安装失败（Ubuntu 26.04+）

```
Failed to install browsers
Error: ERROR: Playwright does not support chromium on ubuntu26.04-x64
```

**解决方法**: 设置 `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` 环境变量后重新安装。

### SOCKS 代理报错

```
ImportError: Using SOCKS proxy, but the 'socksio' package is not installed.
```

**解决方法**: 安装 socks 支持 `pip install httpx[socks]`，或升级到最新版 cnki-mcp-server。

### CNKI 返回 418 或空页面

```
Status: 418
server: TencentEdgeOne
```

**原因**: CNKI 的 CDN（TencentEdgeOne）对服务器/代理 IP 做了反爬拦截。

**解决方法**:
1. 更换代理 IP 或使用住宅 IP
2. 设置 `CNKI_PROXY` 环境变量切换到未被拦截的代理
3. 使用 `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` 避免新版 Ubuntu 兼容问题
4. 确保运行环境能够正常访问 `https://www.cnki.net/`

### 搜索框找不到（#txt_SearchText 超时）

```
Locator.wait_for: Timeout 15000ms exceeded.
waiting for locator("#txt_SearchText") to be visible
```

**原因**: CNKI 首页未正确加载，通常是网络问题或被反爬拦截。

**解决方法**: 先确认在浏览器中能否正常打开 `https://www.cnki.net/`，如果不行则参考上一条「CNKI 返回 418」的解决方案。

## 许可

MIT License
