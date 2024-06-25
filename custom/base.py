import asyncio
import os
import json
import time
from playwright.async_api import async_playwright

# 设置输出目录
istanbul_cli_output = os.path.join(os.getcwd(), '.canyon_output')
os.makedirs(istanbul_cli_output, exist_ok=True)

# 定义测试扩展类
class CustomPlaywrightTest:
    def __init__(self):
        self.playwright = None
        self.browser = None

    async def context(self, context, use):
        # 在每个测试运行前执行的操作
        await context.add_init_script("""
            window.addEventListener('beforeunload', () => {
                window.collectIstanbulCoverage(window.__coverage__, window.__canyon__);
            });
        """)

        await asyncio.gather(
            self.ensure_output_directory(),
            context.expose_function('collectIstanbulCoverage', self.collect_istanbul_coverage),
            use(context)
        )

        # 在每个页面上执行收集覆盖率的操作
        for page in context.pages:
            await page.evaluate('window.collectIstanbulCoverage(window.__coverage__, window.__canyon__);')

    async def ensure_output_directory(self):
        # 确保输出目录存在
        await asyncio.to_thread(os.makedirs, istanbul_cli_output, exist_ok=True)

    async def collect_istanbul_coverage(self, coverage_json, canyon_json):
        # 收集覆盖率数据到输出目录
        if coverage_json and canyon_json:
            filename = os.path.join(istanbul_cli_output, f"{int(time.time() * 1000)}.json")
            with open(filename, 'w') as f:
                json.dump({
                    **canyon_json,
                    'coverage': coverage_json
                }, f)

    async def run_test(self):
        async with async_playwright() as playwright:
            self.playwright = playwright
            browser = await self.playwright.chromium.launch()
            self.browser = browser
            context = await browser.new_context()
            try:
                await self.context(context, lambda ctx: self.test_function(ctx))
            finally:
                await browser.close()

    async def test_function(self, context):
        # 示例测试函数：访问网页并断言
        page = await context.new_page()
        await page.goto('https://todolist-production-c9e8.up.railway.app/')
        title = await page.title()
        assert title == 'TodoMVC: React'

# 创建测试对象实例
custom_test = CustomPlaywrightTest()
