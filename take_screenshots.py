"""自动截取 Streamlit 看板完整页面截图，保存到 screenshots/ 目录。"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

URL = "http://localhost:8501"
OUT = Path("screenshots")
OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"


async def wait_for_render(page, extra_seconds=7):
    await page.wait_for_selector('[data-testid="stApp"]', timeout=30000)
    await asyncio.sleep(extra_seconds)


async def new_tall_page(browser):
    return await browser.new_page(viewport={"width": 1440, "height": 1800})


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path=CHROME)

        # -- screenshot 1: default state, all 500 points --
        print("screenshot 1: default state...")
        p1 = await new_tall_page(browser)
        await p1.goto(URL)
        await wait_for_render(p1)
        await p1.screenshot(path=OUT / "screenshot_1_map_overview.png")
        print("[OK] screenshot_1_map_overview.png")
        await p1.close()

        # -- screenshot 2: sidebar filter band=n78 --
        print("screenshot 2: filter band=n78...")
        p2 = await new_tall_page(browser)
        await p2.goto(URL)
        await wait_for_render(p2)
        selectboxes = await p2.query_selector_all('[data-testid="stSelectbox"]')
        if selectboxes:
            await selectboxes[0].click()
            await asyncio.sleep(1)
            options = await p2.query_selector_all('li[role="option"]')
            for opt in options:
                if "n78" in await opt.inner_text():
                    await opt.click()
                    break
        await asyncio.sleep(5)
        await p2.screenshot(path=OUT / "screenshot_2_sidebar_filter.png")
        print("[OK] screenshot_2_sidebar_filter.png")
        await p2.close()

        # -- screenshot 3: filter terminal=Smartphone --
        print("screenshot 3: filter TerminalType=Smartphone...")
        p3 = await new_tall_page(browser)
        await p3.goto(URL)
        await wait_for_render(p3)
        selectboxes = await p3.query_selector_all('[data-testid="stSelectbox"]')
        if len(selectboxes) >= 2:
            await selectboxes[1].click()
            await asyncio.sleep(1)
            options = await p3.query_selector_all('li[role="option"]')
            for opt in options:
                if "Smartphone" in await opt.inner_text():
                    await opt.click()
                    break
        await asyncio.sleep(5)
        await p3.screenshot(path=OUT / "screenshot_3_smartphone_filter.png")
        print("[OK] screenshot_3_smartphone_filter.png")
        await p3.close()

        await browser.close()
        print(f"All screenshots saved to: {OUT.resolve()}")


asyncio.run(main())
