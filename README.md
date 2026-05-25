# CNKI MCP Server

[![PyPI version](https://img.shields.io/pypi/v/cnki-mcp.svg)](https://pypi.org/project/cnki-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**CNKI (中国知网) MCP Server** — 通过 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 为 AI Agent 提供中文学术论文检索能力。

## 功能

| 工具 | 说明 |
|------|------|
| `search_cnki` | 搜索 CNKI 论文，支持多页、多种搜索类型和排序方式 |
| `get_paper_detail` | 获取论文详情（标题、摘要、作者、关键词、DOI 等 15+ 字段） |
| `find_best_match` | 快速匹配论文标题，验证引用信息 |

### 搜索类型

支持 15 种搜索类型：主题、关键词、篇名、作者、作者单位、全文、DOI、基金、摘要等（中英文别名均可）。

### 排序方式

相关度 / 发表时间 / 被引 / 下载 / 综合（支持英文别名：relevance, date, cited, download, composite）。

## 安装

```bash
# 安装包
pip install cnki-mcp

# 安装 Playwright Chromium 浏览器（首次使用自动安装）
python -m playwright install chromium
```

> **注意**: Playwright Chromium 约 300MB，首次安装需要下载。后续使用无需重复安装。

## 使用

### Claude Code

在 `claude_code_settings.json` 中添加：

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

在 Claude Desktop 配置中添加：

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
- Playwright Chromium（自动安装）

## 技术实现

- **引擎**: Playwright（自带签名 Chromium，跨平台零配置）
- **MCP 框架**: FastMCP
- **并发**: 原生 async/await
- **反检测**: 随机 User-Agent、人类模拟输入、navigator.webdriver 覆写
- **会话复用**: 共享 BrowserContext，Cookie 互通，避免 CNKI 验证码

## 开发

```bash
git clone https://github.com/your-org/cnki-mcp.git
cd cnki-mcp
pip install -e ".[dev]"
python -m playwright install chromium

# 运行测试
pytest tests/ -v
```

## 许可

MIT License

## 致谢

本项目基于原 [cnki-mcp](https://github.com/your-org/cnki-mcp) 重构，引擎从 Selenium 迁移到 Playwright。
