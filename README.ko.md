# Oh My Codex

<p align="center">
  <strong>🚀 OpenAI Codex CLI를 위한 멀티 에이전트 오케스트레이션</strong><br>
  <em>Codex를 AI 에이전트 팀으로 만들어줍니다</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/oh-my-codex/"><img src="https://img.shields.io/pypi/v/oh-my-codex" alt="PyPI"></a>
  <a href="https://github.com/junghwaYang/oh-my-codex/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://github.com/junghwaYang/oh-my-codex"><img src="https://img.shields.io/github/stars/junghwaYang/oh-my-codex" alt="Stars"></a>
</p>

<p align="center">
  <a href="#설치">설치</a> •
  <a href="#빠른-시작">빠른 시작</a> •
  <a href="#실행-모드">모드</a> •
  <a href="#에이전트">에이전트</a> •
  <a href="#도구">도구</a> •
  <a href="README.md">English</a>
</p>

---

## 왜 Oh My Codex?

Codex CLI 혼자도 강력합니다. **Oh My Codex는 이를 팀으로 만들어줍니다.**

| Codex CLI | Oh My Codex |
|-----------|-------------|
| 단일 에이전트 | 32개 전문 에이전트 |
| 수동 모델 선택 | 자동 모델 라우팅 |
| 순차 실행 | 병렬 실행 |
| 세션 메모리 없음 | 세션 저장/재개 |

[Vercel 연구](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) 기반: **AGENTS.md가 100% 통과율** 달성 (스킬만 사용 시 79%)

## 설치

### 방법 1: PyPI (권장)

```bash
pip install oh-my-codex
omx-setup  # 대화형 설정 마법사
```

### 방법 2: pip 전체 설치 (오케스트레이션 포함)

```bash
pip install "oh-my-codex[full]"  # OpenAI Agents SDK 포함
omx-setup
```

### 방법 3: 소스에서

```bash
git clone https://github.com/junghwaYang/oh-my-codex.git
cd oh-my-codex
./install.sh
```

### 방법 4: uv (빠름)

```bash
uv pip install "oh-my-codex[full]"
omx-setup
```

### 필수 요건

- Python 3.10+
- [Codex CLI](https://github.com/openai/codex) 설치됨 (`npm i -g @openai/codex`)
- OpenAI API 키 또는 Codex Pro 구독

## 빠른 시작

```bash
# 기본 사용 (직접 Codex 호출)
omx "auth.py 버그 수정해"

# 멀티 에이전트 자율 실행
omx "autopilot: 인증 기능 있는 REST API 만들어"

# 병렬 실행
omx "ulw: 모든 컴포넌트 TypeScript로 변환"

# 포기 안 하는 모드
omx "ralph: 실패하는 테스트 전부 고쳐"
```

## 실행 모드

| 키워드 | 모드 | 설명 | 에이전트 |
|--------|------|------|----------|
| `autopilot:` | 자율 실행 | 완전 자동 | PM → Executor → Tester → Reviewer |
| `ulw:` | 병렬 실행 | 멀티 에이전트 병렬 | PM + Frontend + Backend + Tester |
| `ultrapilot:` | 최대 병렬 | 모든 전문가 동시 | 전체 스페셜리스트 |
| `team:` | 팀 | 파이프라인 오케스트레이션 | plan → exec → verify → fix 루프 |
| `ralph:` | 끈질긴 | 절대 포기 안 함 | PM → Executor → Debugger |
| `plan:` | 기획 | 실행 없이 계획만 | Planner + Architect |
| `eco:` | 절약 | 토큰 효율적, 빠름 | 단일 Executor |
| `tdd:` | TDD | 테스트 주도 개발 | Tester → Executor |
| `review:` | 리뷰 | 코드 리뷰 | Reviewer + Security |
| `debug:` | 디버그 | 체계적 디버깅 | Debugger + Analyst |

### 예시

```bash
# 복잡한 기능 개발
omx "autopilot: Google, GitHub OAuth2 구현해"

# 병렬 리팩토링
omx "ulw: 모든 클래스 컴포넌트를 훅으로 변환"

# 끈질긴 버그 수정
omx "ralph: 로그인 리다이렉트 안 되는 거 고쳐"

# 아키텍처 기획
omx "plan: 마이크로서비스 아키텍처 설계해"

# 빠른 수정 (토큰 절약)
omx "eco: API 호출에 에러 핸들링 추가"

# 테스트 주도 개발
omx "tdd: 비밀번호 검증 구현"

# 보안 리뷰
omx "review: 인증 모듈 감사해"
```

## 모델 & 추론

### 자동 모델 선택

| 작업 복잡도 | 모델 |
|-------------|------|
| 실시간 | gpt-5.3-codex-spark |
| 단순 | gpt-5-codex-mini |
| 표준 | gpt-5.2-codex |
| 복잡 | gpt-5.3-codex |
| 장기 실행 | gpt-5.1-codex-max |

### 추론 강도 (Reasoning Effort)

| 레벨 | 용도 | 자동 매핑 모드 |
|------|------|----------------|
| `none` | 빠른 응답 | eco |
| `low` | 가벼운 작업 | tdd, pipeline |
| `medium` | 균형 | plan, ultrawork |
| `high` | 깊은 사고 | autopilot, review |
| `xhigh` | 최대 (5.3-codex) | ralph, ultrapilot, debug |

```bash
# 수동 지정
omx --reasoning xhigh "복잡한 아키텍처 결정"
omx --model gpt-5.3-codex "중요한 작업"
```

## 에이전트 (32개)

### 오케스트레이션
| 에이전트 | 모델 | 역할 |
|----------|------|------|
| PM | gpt-5.3-codex | 마스터 오케스트레이터, 작업 위임 |
| Coordinator | gpt-5.3-codex | 병렬 실행 관리 |
| Executor | gpt-5.2-codex | 작업 실행 |

### 개발
| 에이전트 | 전문 분야 |
|----------|-----------|
| Frontend | React, Vue, TypeScript, CSS |
| Backend | Node.js, Python, API, DB |
| Fullstack | 엔드투엔드 개발 |
| Mobile | React Native, Flutter |
| DevOps | CI/CD, Docker, K8s |

### 품질
| 에이전트 | 집중 영역 |
|----------|-----------|
| Tester | 유닛, 통합, E2E 테스트 |
| Reviewer | 코드 리뷰, 베스트 프랙티스 |
| Security | 취약점, OWASP |
| Debugger | 체계적 버그 추적 |

### 전문가
| 에이전트 | 도메인 |
|----------|--------|
| Architect | 시스템 설계, 패턴 |
| Researcher | 정보 수집 |
| Data/ML | 데이터 엔지니어링, ML |
| Writer | 문서화 |

## 도구 (9개)

에이전트가 사용할 수 있는 도구:

| 도구 | 설명 |
|------|------|
| `run_shell` | 터미널 명령 실행 |
| `read_file` | 파일 내용 읽기 |
| `write_file` | 파일 생성/덮어쓰기 |
| `edit_file` | 정확한 텍스트 교체 |
| `list_directory` | 디렉토리 탐색 |
| `search_files` | 파일명/내용 검색 |
| `git_status` | Git 상태 확인 |
| `git_diff` | 변경사항 보기 |
| `run_tests` | 테스트 자동 감지 & 실행 |

## 스킬 (31개)

`~/.codex/skills/`에 설치됨:

| 카테고리 | 스킬 |
|----------|------|
| 오케스트레이션 | team, autopilot, ultrawork, ultrapilot, ralph, pipeline, swarm |
| 기획 | planner, ralplan, analyze, research, deepsearch |
| 개발 | eco, tdd, build-fix, deepinit, release |
| 품질 | reviewer, code-review, security-review, ultraqa |
| 유틸리티 | git-master, playwright, debug, mcp-setup, doctor, hud, trace |

## CLI 레퍼런스

```bash
# 기본
omx "작업"                        # 모드 자동 감지
omx "autopilot: 작업"             # 명시적 모드

# 옵션
omx --model gpt-5.3-codex "작업"  # 모델 지정
omx --reasoning high "작업"       # 추론 레벨
omx --provider openai "작업"      # API 과금 사용
omx -v "작업"                     # 상세 출력

# 세션
omx --list                        # 모든 세션 목록
omx --resume <session_id>         # 세션 재개
omx --status                      # 현재 설정 표시

# 설정
omx-setup                         # 설정 마법사 실행
omx --set-provider codex          # 빌링 변경
```

## 설정

### ~/.codex/omx-config.yaml

```yaml
billing:
  provider: codex  # 또는 "openai"

model:
  default: gpt-5.3-codex
  routing:
    spark: gpt-5.3-codex-spark
    mini: gpt-5-codex-mini
    standard: gpt-5.2-codex
    powerful: gpt-5.3-codex
    max: gpt-5.1-codex-max
  reasoning:
    default: none
    autopilot: high
    ralph: xhigh
    eco: none

skills:
  auto_load: true
```

## 아키텍처

```
사용자: omx "autopilot: API 만들어"
              │
              ▼
       ┌─────────────┐
       │ 모드 감지    │ → autopilot
       │ 모델 라우팅  │ → gpt-5.3-codex
       │ 추론 레벨   │ → high
       └──────┬──────┘
              ▼
       ┌─────────────┐
       │ PM 에이전트  │ ← 도구: shell, files, git
       │ + Handoffs  │ → [Executor, Tester, Reviewer]
       └──────┬──────┘
              ▼
       ┌─────────────┐
       │ Runner.run  │ ← OpenAI Agents SDK
       │ 자율 실행    │
       └──────┬──────┘
              ▼
          결과 반환
```

## 비교

| 기능 | Codex CLI | omx |
|------|-----------|-----|
| 단일 에이전트 | ✅ | ✅ |
| 멀티 에이전트 | ❌ | ✅ 32개 |
| 병렬 실행 | ❌ | ✅ ultrawork |
| 자동 모델 라우팅 | ❌ | ✅ |
| 추론 제어 | 수동 | ✅ 자동 매핑 |
| 세션 저장 | ❌ | ✅ |
| 스킬 | ✅ | ✅ 31개 포함 |

## 크레딧

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — 원본 영감
- [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) — 멀티 에이전트 프레임워크
- [Vercel 연구](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — AGENTS.md 철학

## 라이선스

MIT © [junghwaYang](https://github.com/junghwaYang)
