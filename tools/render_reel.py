"""릴스용 세로 영상(1080x1920, 30fps) 렌더링.

준비:
  pip install playwright
  playwright install chromium
  ffmpeg 설치 (brew install ffmpeg / winget install ffmpeg)

실행:
  python tools/render_reel.py          # out/pool_reels.mp4 생성
  python tools/render_reel.py test     # 확인용 프레임 몇 장만 out/ 에 저장
"""
import asyncio
import subprocess
import sys
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
REEL = (ROOT / "tools" / "reel.html").as_uri()
OUT = ROOT / "out"

FPS = 30
DUR = 30.0          # 영상 길이(초)
H0, H1 = 5.2, 21.0  # 시작/끝 시각


def ease(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def cam(t):
    """카메라 x 위치: 처음 4초는 출발대, 이후 오른쪽 끝까지 천천히 이동."""
    a, b = 60.0, 761.25
    return a + (b - a) * ease((t - 4) / 21)


async def main(mode):
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        br = await p.chromium.launch()
        pg = await br.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto(REEL)
        await pg.wait_for_function("window.ready")
        await pg.wait_for_timeout(500)
        await pg.evaluate(f"()=>{{for(let i=0;i<30;i++)step({H0},1/30,{cam(0)});}}")
        n = int(DUR * FPS)
        tmp = OUT / "pool_reels.tmp.mp4"
        ff = None
        if mode != "test":
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                 "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                 "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(tmp)],
                stdin=subprocess.PIPE)
        for f in range(n):
            t = f / FPS
            h = H0 + (H1 - H0) * t / DUR
            await pg.evaluate(f"step({h},{1 / FPS},{cam(t)})")
            if mode == "test":
                if f in (0, 60, n // 2, n - 1):
                    await pg.screenshot(path=str(OUT / f"frame_{f:04d}.jpg"), type="jpeg", quality=92)
            else:
                ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
        await br.close()
        if ff:
            ff.stdin.close()
            if ff.wait() == 0:
                tmp.replace(OUT / "pool_reels.mp4")
                print("완료:", OUT / "pool_reels.mp4")
            else:
                print("ffmpeg 실패")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "full"))
