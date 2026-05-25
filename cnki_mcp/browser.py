"""
AsyncPlaywright 浏览器池管理。

特性:
- 懒初始化：首次调用时才启动浏览器
- 实例复用：多次调用共享同一 browser 实例
- 共享 BrowserContext：同一 context 内创建 Page，Cookie 互通
- 空闲超时关闭（600s）
- asyncio.Lock 保护并发访问
"""

import asyncio
import random
import subprocess
import sys
import time
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from cnki_mcp.config import (
    BROWSER_TIMEOUT,
    IDLE_TIMEOUT,
    USER_AGENTS,
)
from cnki_mcp.exceptions import BrowserError


class AsyncBrowserPool:
    """异步 Playwright 浏览器池（共享 BrowserContext，Cookie 互通）"""

    def __init__(self) -> None:
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._last_used: float = 0
        self._lock = asyncio.Lock()

    async def _ensure_browser(self) -> Browser:
        """确保浏览器实例可用"""
        if self._browser is not None:
            if time.time() - self._last_used > IDLE_TIMEOUT:
                await self._close_browser()
            elif not self._browser.is_connected():
                self._browser = None
                self._context = None

        if self._browser is None:
            try:
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                        "--disable-infobars",
                        "--disable-extensions",
                    ],
                )
            except Exception as e:
                if "Executable doesn't exist" in str(e) or "playwright" in str(e).lower():
                    await self._install_browser()
                    self._playwright = await async_playwright().start()
                    self._browser = await self._playwright.chromium.launch(
                        headless=True,
                        args=[
                            "--disable-blink-features=AutomationControlled",
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                        ],
                    )
                else:
                    raise BrowserError(f"浏览器启动失败: {e}") from e

            if self._browser is None:
                raise BrowserError("浏览器启动失败")

            # 创建共享的 BrowserContext
            self._context = await self._browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={"width": 1920, "height": 1080},
                locale="zh-CN",
            )
            await self._context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
            """)

        self._last_used = time.time()
        return self._browser

    async def _install_browser(self) -> None:
        """安装 Playwright Chromium"""
        try:
            subprocess.check_call(
                [sys.executable, "-m", "playwright", "install", "chromium"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )
        except subprocess.CalledProcessError as e:
            raise BrowserError(
                "Playwright Chromium 安装失败。请手动运行: playwright install chromium"
            ) from e

    async def new_page(self) -> Page:
        """创建新 Page（共享 Context，Cookie 互通）"""
        async with self._lock:
            await self._ensure_browser()

        assert self._context is not None
        page = await self._context.new_page()
        page.set_default_timeout(BROWSER_TIMEOUT)
        return page

    async def navigate_to_cnki(self, page: Page) -> None:
        """导航到 CNKI 首页（含弹窗处理）"""
        await page.goto("https://www.cnki.net/", wait_until="domcontentloaded")
        await asyncio.sleep(random.uniform(1, 2))
        await self._dismiss_popups(page)

    async def _dismiss_popups(self, page: Page) -> bool:
        """尝试关闭 CNKI 弹窗/遮罩"""
        dismiss_selectors = [
            "#close",
            ".close",
            'div[class*="popup"] a:has-text("关闭")',
            'div[class*="modal"] button:has-text("关闭")',
            'div[class*="layui-layer"] a[class*="layui-layer-close"]',
        ]
        for selector in dismiss_selectors:
            try:
                elem = page.locator(selector).first
                if await elem.count() > 0 and await elem.is_visible():
                    await elem.click()
                    await asyncio.sleep(0.5)
                    return True
            except Exception:
                continue
        return False

    async def _close_browser(self) -> None:
        """关闭浏览器实例和上下文"""
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

    async def close(self) -> None:
        """关闭浏览器池"""
        async with self._lock:
            await self._close_browser()
