# Oh My Codex

<p align="center">
  <strong>OpenAI Codex CLI를 위한 멀티에이전트 오케스트레이션 시스템</strong>
</p>

<p align="center">
  <a href="#특징">특징</a> •
  <a href="#빠른-시작">빠른 시작</a> •
  <a href="#실행-모드">실행 모드</a> •
  <a href="#스킬">스킬</a> •
  <a href="#멀티에이전트-오케스트레이션">멀티에이전트</a> •
  <a href="README.md">English</a>
</p>

---

[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)에서 영감을 받아, OpenAI Codex CLI 아키텍처에 맞게 구현했습니다.

## 왜 Oh My Codex인가?

OpenAI Codex CLI는 강력하지만, Claude Code + oh-my-claudecode가 제공하는 멀티에이전트 오케스트레이션 기능이 없습니다. 이 프로젝트는 그 간극을 메웁니다.

[Vercel 리서치](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)에 따르면 **AGENTS.md가 스킬보다 성능이 좋습니다** (100% vs 79% 통과율). 그래서 핵심 오케스트레이션 로직이 항상 컨텍스트에 있는 AGENTS.md-First 설계를 사용합니다.

## 특징

| 특징 | 설명 |
|------|------|
| 🧠 **AGENTS.md-First** | 핵심 오케스트레이션 로직이 항상 컨텍스트에 있음 |
| 🚀 **5가지 실행 모드** | autopilot, ultrawork, plan, eco, review |
| 🔧 **8개 기본 스킬** | Git, Playwright, Debug 등 |
| 🤖 **멀티에이전트** | PM + 전문 에이전트 (Codex MCP + Agents SDK) |
| 📊 **스마트 라우팅** | 작업 복잡도 기반 자동 모델 선택 |
| 💾 **세션 관리** | 장시간 작업 일시정지, 재개, 추적 |
| ⚡ **CLI 래퍼** | 키워드 감지 기능이 있는 `omc` 명령어 |

## 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/siltarre/oh-my-codex.git
cd oh-my-codex

# 설치 스크립트 실행
./install.sh
```

설치 스크립트가 하는 일:
- `~/.codex/skills/`에 스킬 설치
- `~/.codex/config.toml`에 설정 복사
- `~/.local/bin/`에 `omc` CLI 설치
- (선택) Python 오케스트레이터 설치

### 기본 사용법

```bash
# Autopilot 모드 — 완전 자율 실행
omc "autopilot: 태스크 관리용 REST API 만들어줘"

# Ultrawork 모드 — 병렬 멀티파일 작업
omc "ulw: 모든 파일에서 'userId'를 'user_id'로 변경해줘"

# Plan 모드 — 인터뷰와 설계 (실행 없음)
omc "plan: 결제 시스템 아키텍처 설계하자"

# Eco 모드 — 토큰 효율적, 빠른 작업
omc "eco: gitignore에 .env 추가해줘"

# 직접 전달 (키워드 없음 = Codex 직접 호출)
omc "auth.py 버그 고쳐줘"
```

## 실행 모드

### Autopilot (`autopilot:`)

완전 자율 실행 모드. 에이전트가:
1. 작업을 분석하고 상세 계획 생성
2. 각 단계를 독립적으로 실행
3. 결과를 수락 기준과 대조하여 검증
4. 완료될 때까지 반복 (또는 도움 요청)

**적합한 작업:** 기능 개발, 복잡한 구현, 다단계 작업

```bash
omc "autopilot: JWT 기반 사용자 인증 구현해줘. 로그인, 로그아웃, 토큰 갱신 포함"
```

### Ultrawork (`ulw:`)

대규모 작업을 위한 병렬 실행 모드. 작업을 독립적인 단위로 분해하고 동시에 처리합니다.

**적합한 작업:** 리팩토링, 대량 업데이트, 코드베이스 전체 변경

```bash
omc "ulw: src/utils/ 아래 모든 유틸리티 함수에 TypeScript 타입 추가해줘"
```

### Plan (`plan:`)

실행 없이 인터뷰 기반 계획만 수립. 명확화 질문을 하고 종합적인 계획 문서를 생성합니다.

**적합한 작업:** 아키텍처 설계, 프로젝트 시작, 복잡한 요구사항

```bash
omc "plan: 실시간 협업 문서 에디터 설계하자"
```

### Eco (`eco:`)

간단한 작업을 위한 토큰 효율 모드. 최소 출력, 직접 실행, 빠른 완료.

**적합한 작업:** 빠른 수정, 간단한 변경, 루틴 작업

```bash
omc "eco: package.json 버전을 2.0.0으로 업데이트해줘"
```

### Ralph (`ralph:`)

포기하지 않는 지속적 autopilot. 작업이 정말로 완료될 때까지 계속 시도합니다.

**적합한 작업:** 고집스러운 버그, 복잡한 디버깅, 끈기가 필요한 작업

```bash
omc "ralph: 프로젝트의 모든 TypeScript 에러 고쳐줘"
```

## 스킬

스킬은 Codex가 필요할 때 로드하는 전문화된 지시 세트입니다. Oh My Codex에는 8개의 기본 스킬이 포함되어 있습니다:

| 스킬 | 설명 | 트리거 |
|------|------|--------|
| **autopilot** | 자율 기능 개발 | `autopilot:` 키워드 |
| **ultrawork** | 병렬 멀티파일 작업 | `ulw:` 키워드 |
| **planner** | 인터뷰 기반 계획 수립 | `plan:` 키워드 |
| **eco** | 토큰 효율적 실행 | `eco:` 키워드 |
| **reviewer** | 보안/성능 체크리스트 코드 리뷰 | PR/리뷰 시 자동 |
| **git-master** | Git 워크플로우 (rebase, cherry-pick 등) | Git 관련 작업 |
| **playwright** | E2E 테스트와 브라우저 자동화 | 테스트 작업 |
| **debug** | 체계적인 디버깅 방법론 | 디버깅 작업 |

### 외부 스킬 설치

```bash
# skills.sh 레지스트리에서
npx skills add supabase/supabase-postgres-best-practices

# 스킬은 ~/.codex/skills/에 설치됩니다
```

## 멀티에이전트 오케스트레이션

복잡한 모드(autopilot, ultrawork)를 사용할 때, Oh My Codex는 전문 에이전트를 생성할 수 있습니다:

```
┌─────────────────────────────────────────────────────────┐
│                   프로젝트 매니저                          │
│              (조율, 위임, 검증)                            │
└─────────────────────┬───────────────────────────────────┘
                      │
       ┌──────────────┼──────────────┬──────────────┐
       ▼              ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  프론트엔드  │ │   백엔드    │ │  QA 테스터  │ │   리뷰어    │
│   개발자    │ │   개발자    │ │             │ │             │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
     React         API           테스트          보안
     TypeScript    데이터베이스    엣지 케이스     성능
     CSS           인증           커버리지        품질
```

**요구사항:** `pip install oh-my-codex[full]`

각 에이전트는 전문화된 지시를 가지며 MCP를 통해 Codex CLI 도구를 사용할 수 있습니다.

## 아키텍처

```
oh-my-codex/
├── AGENTS.md                 # 🧠 핵심 오케스트레이션 두뇌
│                             #    항상 로드됨, 라우팅 로직 포함
├── .codex/skills/            # 🔧 네이티브 Codex 스킬
│   ├── autopilot/            #    완전 자율 모드
│   ├── ultrawork/            #    병렬 실행
│   ├── planner/              #    인터뷰 & 계획
│   ├── eco/                  #    토큰 효율
│   ├── reviewer/             #    코드 리뷰 + references/
│   ├── git-master/           #    Git 워크플로우
│   ├── playwright/           #    E2E 테스트
│   └── debug/                #    체계적 디버깅
│
├── orchestrator/             # 🤖 Python 멀티에이전트 시스템
│   ├── main.py               #    오케스트레이터 진입점
│   ├── agents/               #    에이전트 정의 (PM, Frontend 등)
│   │   └── base.py           #    에이전트 설정과 지시
│   ├── session.py            #    세션 영속성
│   ├── mcp.py                #    MCP 서버 설정
│   ├── router.py             #    작업 분류 & 모델 라우팅
│   ├── utils.py              #    헬퍼 유틸리티
│   └── cli.py                #    CLI 진입점
│
├── bin/omc                   # ⚡ CLI 래퍼 스크립트
├── config.toml               # ⚙️ Codex 설정
├── pyproject.toml            # 📦 Python 패키지 정의
└── install.sh                # 🚀 원클릭 설치 스크립트
```

## 설정

### ~/.codex/config.toml

```toml
[model]
default = "o3"

# 복잡도별 모델 라우팅
[model.routing]
simple = "gpt-4.1-mini"    # 간단한 작업, eco 모드
standard = "gpt-4.1"       # 일반 작업
complex = "o3"             # 아키텍처, 멀티에이전트

[skills]
auto_load = true           # 매칭되는 스킬 자동 로드

[compaction]
enabled = true             # 긴 세션에서 활성화
threshold_tokens = 100000
```

### MCP 서버 설정

```toml
[mcp.github]
command = "npx"
args = ["-y", "@anthropic/mcp-server-github"]
env = { GITHUB_TOKEN = "your-token" }

[mcp.postgres]
command = "npx"
args = ["-y", "@anthropic/mcp-server-postgres", "postgresql://..."]
```

## CLI 레퍼런스

```bash
# 모드 감지로 실행
omc "autopilot: X 기능 만들어줘"

# 특정 모드 강제
omc -m ultrawork "유틸 리팩토링해줘"

# 모델 지정
omc --model gpt-4.1 "간단한 작업"

# 세션 관리
omc --list                    # 모든 세션 목록
omc --resume <session-id>     # 일시정지된 세션 재개

# 상태와 진단
omc --status                  # 설치 상태 확인

# 직접 Codex (오케스트레이션 건너뛰기)
omc --direct "빠른 수정"

# 상세 출력
omc -v "autopilot: 복잡한 작업"
```

## 설계 철학

### 왜 AGENTS.md-First인가?

Vercel 리서치에 따르면, 압축된 문서 인덱스가 있는 AGENTS.md를 사용한 에이전트가 **100% 작업 완료율**을 달성한 반면, 스킬 기반 검색은 명시적 지시에도 **79%**에 그쳤습니다.

핵심 인사이트: **항상 컨텍스트에 있는 정보가 필요할 때 검색하는 것보다 낫습니다.**

에이전트가 무언가를 찾아볼지 결정할 필요가 없습니다 — 정보가 항상 거기 있습니다.

### 스킬 라우팅 모범 사례

[OpenAI 가이드라인](https://developers.openai.com/blog/skills-shell-tips)에서:

1. **description을 라우팅 로직처럼 작성** — 마케팅 카피가 아니라
2. **"사용하지 말 것" 섹션 포함** — 오용 방지
3. **부정 예시 추가** — 잘못된 트리거 감소
4. **템플릿은 스킬 안에** — 필요할 때만 로드됨

## 세션 관리

Oh My Codex는 장시간 작업을 추적합니다:

```bash
# 복잡한 작업에서 세션이 자동 생성됨
omc "autopilot: 인증 시스템 만들어줘"
# → Session: 20260213_143022_a1b2c3d4

# 세션 목록
omc --list
# ID                          Status      Mode        Task
# 20260213_143022_a1b2c3d4    active      autopilot   인증 시스템...

# 중단되면 재개
omc --resume 20260213_143022_a1b2c3d4
```

세션은 `~/.codex/sessions/`에 JSON으로 저장됩니다.

## 문제 해결

### `omc: command not found`

`~/.local/bin`을 PATH에 추가하세요:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

`~/.zshrc` 또는 `~/.bashrc`에 추가하세요.

### 멀티에이전트가 작동하지 않음

전체 패키지를 설치하세요:

```bash
pip install -e ".[full]"
```

### 스킬이 로드되지 않음

설치를 확인하세요:

```bash
omc --status
ls ~/.codex/skills/
```

## 로드맵

- [x] Phase 1: Skills + AGENTS.md 코어
- [x] Phase 2: Agents SDK 기반 Python 오케스트레이터
- [x] Phase 3: 모델 라우팅 & 작업 분류
- [x] Phase 4: CLI 래퍼 (`omc`) + 세션 관리
- [ ] Phase 5: 네이티브 Codex 플러그인 (Codex 플러그인 시스템 대기 중)

## 기여

기여를 환영합니다! 다음 절차를 따라주세요:

1. 저장소 포크
2. 기능 브랜치 생성
3. 변경 사항 작성
4. 풀 리퀘스트 제출

## 크레딧

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — 원본 영감
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — 아키텍처 참조
- [Supabase Agent Skills](https://github.com/supabase/agent-skills) — 스킬 구조 표준
- [Vercel AGENTS.md Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — 설계 철학

## 라이선스

MIT © 2026 tarae
