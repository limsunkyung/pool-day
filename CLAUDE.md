# 동네 수영장의 하루 (pool-day)

새벽 5시~저녁 9시 동안 실내수영장 풍경이 바뀌는 SVG 라인아트 애니메이션 웹페이지.
GitHub Pages로 배포한다 (main 브랜치 루트의 index.html).

## 현재 구조
- `index.html` — 페이지 전체(HTML·CSS·JS 한 파일). 빌드 도구 없음.
  - 화면 비율에 따라 가로/세로 레이아웃 자동 전환 (`layout()`): 세로는 벽(창문) 영역을 잘라 쓰고 바닥·풀 그룹(`#deckG`)을 90° 회전.
  - 시간대별 색: `K` 키프레임 배열 → CSS 변수(`--sky1`, `--wall`, `--water` …)로 주입. 선 색(`--ink`)은 벽 밝기로 자동 결정.
  - 레인 설정: `LANES` 배열 (레인별 속도·영법 목록). 영법: `free` `fly` `breast` `kick` `start`(출발대 다이빙, 2번 레인).
  - 수영 경로: `pos()` — 한 방향 순환(우측통행), 양 끝 턴. 그리기: `drawSwimmer()`, 다이빙 상태머신: `updStarter()`.
- `tools/reel.html` — 릴스용 9:16 버전(컨트롤 없음, `window.step(h, dt, camX)`로 프레임 단위 구동).
- `tools/render_reel.py` — Playwright + ffmpeg로 `out/pool_reels.mp4` 생성.
- `database.rules.json` — Firebase Realtime Database 보안 규칙(아래 "실시간 공유 보안" 참고). 콘솔 Rules 탭에 그대로 붙여넣는다.

## 작업 규칙
- 화면에 글자는 왼쪽 위 시간 표시만 둔다 (레인 이름·소품 라벨 넣지 않기).
- 레인: 1 초급(킥판) / 2 출발대 스타트 / 3 마스터즈(전원 접영) / 4 연수 / 5 자유. 창밖은 건물 사이 노란 은행나무.
- 바꾼 뒤에는 가로(1240×900)와 세로(390×844) 두 크기로 스크린샷을 찍어 확인한다.
- 커밋 메시지는 한국어로 짧게.

## UI 디자인 원칙 (수영장 그림 바깥 UI)
- 모티프는 "수영장 벽 안내판/스코어보드". 레인 선택은 타일 줄눈(grid gap)으로 나뉜 게시판 타일이고, 게시판·입장 카드 네 모서리에는 볼트 점을 둬 벽에 거는 표지판 느낌을 낸다 (`.frameWrap`, `.modalCard` 공통 배경 패턴).
- 색은 새 변수를 만들지 않고 기존 시간대 변수(`--wall`, `--wall2`, `--frame`, `--ink`, `--sun`)를 `color-mix()`로 배합해서 쓴다. 페이지 배경·컨트롤 패널·입장 카드까지 전부 scene과 같은 시간대 색으로 바뀌어야 한다. 레인로프 색(빨강·파랑·노랑)은 선택된 레인 타일 밑줄 3px 정도로만 아주 작게 쓴다.
- 폰트는 한글 Gowun Dodum + 숫자 전용 VT323(디지털 스코어보드 느낌) 조합. 시계·레인 번호처럼 "숫자"인 곳에만 VT323을 쓰고 본문·라벨은 Gowun Dodum 그대로.
- 상태는 색 반전으로 표현한다: 미선택 = 저대비 아웃라인 타일, 선택됨 = `--ink`/`--wall2` 반전("점등"). 입장 가능해지면 입장 버튼만 `--sun` 색으로 점등.
- 이모지 금지.

## 다음에 할 일 (로드맵)
1. **파일 분리**: index.html을 `css/`, `js/`(palette, scene, swimmers, gear, ui)로 나누고 ES 모듈로. 기능이 늘기 전에 먼저.
2. **방문자 선택 옵션**: 시작 화면에서 이름·레인(1~5)·영법·복장을 고르면 "내 수영자"가 해당 레인에 들어가 강조 표시됨 (구현됨).
   - 도구(킥판·패들·롱핀·숏핀·스노클) 선택 UI는 한 번 넣었다가 마음에 안 들어서 뺐다 — 다시 시도한다면 손·발 끝 좌표를 따라다니게 그리는 게 핵심(머리 옆에 고정하면 안 됨).
   - **복장(수영복·수모) 패턴**: 사진 업로드는 보류(모더레이션·저장 이슈로). 대신 `WEAR_FAMILIES`(스트라이프·도트·체크·컬러블록·타이다이·플로럴·레오파드·카모·그라데이션·셰브론·아가일·컨페티, 13개 틀) × `WEAR_PALETTES`(12개 배색) = 150+ 조합을 `WEAR_COMBOS`로 미리 만들어두고, 입장 모달에는 "아무거나" + 매번 랜덤 7개만 보여줌(`sampleUniqueFamilyWear`가 틀을 먼저 서로 다르게 고른 뒤 틀마다 배색 하나씩 뽑아서, 같은 틀 이름이 색만 다르게 두 번 보이는 일이 없게 함. 페이지 로드마다 다시 섞임). 고른 조합은 방문자별로 `<pattern>`/`<linearGradient>`를 `ensureWearDef()`가 1회만 만들어 재사용(같은 조합 고른 사람끼리 defs 공유). `back`(배영) 스타일은 얼굴(SKIN)은 그대로 두고 수모 조각·수영복에만 패턴이 입혀짐.
   - 이름은 간단한 금칙어 목록(`BAD_WORDS`/`hasBadWord`)에 걸리면 입장을 막고 안내 문구만 보여준다.
   - 세로 모드에서는 `#deckG` 전체가 90° 회전하므로, 이름 말풍선(`sw.bubble`)은 `bub()`에서 `PORTRAIT`일 때 자기 자신에 `rotate(-90)`을 더해 부모 회전을 상쇄한다 — 글자는 항상 똑바로 보인다.
3. **녹화·공유**: `#fsBtn` 누르면 실제로 10초짜리 영상이 만들어져 자동 다운로드(또는 모바일 공유 시트)된다 (구현됨).
   - 매 프레임 `#scene` SVG를 클론 → CSS 변수(`var(--ink)` 등) 쓰던 곳을 현재 리터럴 색상 값으로 치환한 `<style>`을 주입(`svgSnapshotDataUrl()`) → `data:image/svg+xml` → `Image`로 디코드 → `<canvas>`에 `drawImage`. 이 과정을 `loop()` 안에서 `REC_FPS`(18fps) 간격으로 반복(`captureFrameInto`).
   - `canvas.captureStream(REC_FPS)` + `MediaRecorder`로 녹화. mimeType은 `video/mp4;codecs=avc1` → `video/webm;codecs=vp9` 순으로 지원 여부 확인(`pickRecMime`). MediaRecorder/captureStream을 아예 못 쓰는 브라우저면 `activeRecState`가 null이 되고 녹화 없이 전체화면 클린뷰만 동작(방문자가 자기 화면을 직접 녹화하는 걸로 대체).
   - 10초 뒤 자동 종료, 또는 10초 전에 화면 아무 데나 탭하면 조기 종료(`endFsRecording`). 끝나면 `navigator.share`(파일 공유 가능하면 모바일 공유 시트) → 안 되면 `<a download>`로 바로 다운로드.
   - `requestFullscreen()`과 1px 스크롤 트릭은 녹화 중에도 UI를 깨끗하게 숨겨두는 용도로 같이 씀(녹화 자체는 캔버스 내용만 들어가서 브라우저 주소창 노출 여부와 무관하지만, 화면이 지저분하면 사용 경험이 나쁘니 유지).
   - (참고) 개발자용으로는 `tools/render_reel.py`가 이미 Playwright+ffmpeg로 9:16 30초 mp4를 서버에서 만들어줌 — 이건 방문자용 아님, 로컬 실행 전용.
4. **여러 방문자 동시 접속**: Firebase Realtime Database로 구현됨. 자세한 건 아래 "실시간 공유 보안" 참고.

## 실시간 공유 보안 (Firebase)
- 입장 시 `signInAnonymously`로 익명 로그인하고, `swimmers/{내 uid}` 경로 하나에만 내 정보를 `set()`으로 씀(1인 1개, `push` 안 씀). 퇴장하면 그 경로를 `remove()`.
- 보안 규칙은 `database.rules.json`에 있고, 콘솔 Realtime Database → Rules 탭에 그대로 붙여넣어 Publish하면 된다:
  - `swimmers`는 전체 읽기 공개.
  - `swimmers/$uid`는 로그인한 본인(`auth.uid === $uid`)만 쓸 수 있음.
  - `name`(1~4자) · `lane`(0~4) · `style`(허용 영법 목록) · `wear`(40자 이하 문자열, 없어도 됨) · `gender`(`f`/`m`) · `t`(숫자) 외의 필드는 거부, 루트 읽기·쓰기도 잠겨 있음.
- 콘솔에서 해야 할 설정(코드만으로는 안 됨): Authentication → Sign-in method → **Anonymous** 활성화. 꺼져 있으면 로그인이 실패하고 자동으로 "나만 보이는 로컬 모드"로 폴백된다(화면엔 티가 안 남).
- 클라이언트도 받은 데이터를 한 번 더 검증(`validSnap`)하고, `t`가 30분 넘게 갱신 안 된 항목은 화면에서 무시(`isFresh`/`STALE_MS`).
- 이름 금칙어 필터(`BAD_WORDS`)는 클라이언트 단에서만 막는 간단한 목록 — 서버 규칙으로 욕설 자체를 막지는 못하므로(문자열 내용 검사는 RTDB 규칙 문법상 비실용적), 100% 방어는 아니다.
