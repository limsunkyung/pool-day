"""index.html을 가로/세로 두 크기로 캡처해 out/에 저장.

준비:
  pip install playwright
  playwright install chromium

실행:
  python tools/screenshot.py           # 가로+세로 둘 다
  python tools/screenshot.py landscape  # 가로만
  python tools/screenshot.py portrait   # 세로만

옵션:
  --hour=14.5     시간 고정 (기본 14.5, 한낮)
  --hash=lane3    URL 해시 지정 (예: #lane3 → 3번 레인에 '나' 입장)
  --wait=2.5      해시 적용 후 스크린샷 전 실시간 대기 초(기본 2.5, 입수 동작이 진행되도록)
"""
import asyncio
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGE = (ROOT / "index.html").as_uri()
OUT = ROOT / "out"

SIZES = {
    "landscape": (1240, 900),
    "portrait": (390, 844),
}


async def shoot(p, name, width, height, hour, hash_, wait):
    br = await p.chromium.launch()
    pg = await br.new_page(viewport={"width": width, "height": height})
    url = f"{PAGE}#{hash_}" if hash_ else PAGE
    await pg.goto(url)
    await pg.wait_for_timeout(300)
    if hash_:
        await pg.wait_for_timeout(int(wait * 1000))
    if hour is not None:
        # 재생을 멈추고 시간 슬라이더(#scrub)를 직접 설정해 그 시각으로 고정한다.
        await pg.evaluate(f"""() => {{
          const scrub = document.getElementById('scrub');
          const playBtn = document.getElementById('play');
          if (playBtn && playBtn.classList.contains('on')) playBtn.click();
          scrub.value = {hour};
          scrub.dispatchEvent(new Event('input', {{bubbles: true}}));
        }}""")
        await pg.wait_for_timeout(200)
    out_path = OUT / f"{name}.png"
    await pg.screenshot(path=str(out_path))
    await br.close()
    print("저장:", out_path)


async def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    hour, hash_, wait = None, None, 2.5
    for a in sys.argv[1:]:
        if a.startswith("--hour="):
            hour = float(a.split("=", 1)[1])
        elif a.startswith("--hash="):
            hash_ = a.split("=", 1)[1]
        elif a.startswith("--wait="):
            wait = float(a.split("=", 1)[1])
    targets = args if args else list(SIZES)
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        for name in targets:
            w, h = SIZES[name]
            await shoot(p, name, w, h, hour, hash_, wait)


if __name__ == "__main__":
    asyncio.run(main())
