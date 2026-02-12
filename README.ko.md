# Oh My Codex

<p align="center">
  <strong>OpenAI Codex CLI를 위한 멀티에이전트 오케스트레이션 시스템</strong>
</p>

<p align="center">
  <a href="#특징">특징</a> •
  <a href="#빠른-시작">빠른 시작</a> •
  <a href="#실행-모드">실행 모드</a> •
  <a href="#스킬">스킬</a> •
  <a href="#에이전트">에이전트</a> •
  <a href="README.md">English</a>
</p>

---

[oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)에서 영감을 받아 OpenAI Codex CLI용으로 구현.

## 왜 Oh My Codex?

OpenAI Codex CLI는 강력하지만, Claude Code + oh-my-claudecode의 멀티에이전트 오케스트레이션 기능이 없습니다. 이 프로젝트가 그 간극을 메웁니다.

[Vercel 리서치](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)에 따르면 **AGENTS.md가 스킬보다 성능이 좋습니다** (100% vs 79%). 그래서 AGENTS.md-First 설계를 사용합니다.

## 특징

| 특징 | 설명 |
|------|------|
| 🧠 **AGENTS.md-First** | 핵심 오케스트레이션이 항상 컨텍스트에 있음 |
| 🚀 **8가지 실행 모드** | team, autopilot, ultrawork, ralph, pipeline, eco, plan, ultrapilot |
| 🔧 **31개 스킬** | oh-my-claudecode와 동등한 기능 |
| 🤖 **32개 에이전트** | PM부터 데이터 사이언티스트까지 |
| 📊 **스마트 라우팅** | 자동 모델 선택 |
| 💾 **세션 관리** | 일시정지, 재개, 추적 |
| 📡 **HUD & 트레이싱** | 실시간 메트릭과 디버깅 |

## 빠른 시작

```bash
# 클론
git clone https://github.com/junghwaYang/oh-my-codex.git
cd oh-my-codex

# 설치
./install.sh

# 사용
omx "autopilot: REST API 만들어줘"
```

## 실행 모드

| 모드 | 키워드 | 설명 |
|------|--------|------|
| **Team** | `team:` | 멀티에이전트 파이프라인 (plan→exec→verify→fix) |
| **Autopilot** | `autopilot:` | 완전 자율 실행 |
| **Ultrawork** | `ulw:` | 병렬 멀티파일 작업 |
| **Ralph** | `ralph:` | 지속 모드 (포기 안 함) |
| **Ultrapilot** | `ultrapilot:` | 최대 병렬화 |
| **Pipeline** | `pipeline:` | 순차적 단계 처리 |
| **Eco** | `eco:` | 토큰 효율적 실행 |
| **Plan** | `plan:` | 인터뷰 기반 계획 |

### 예시

```bash
# Team 오케스트레이션 (복잡한 작업에 추천)
omx "team: 인증 포함 풀스택 앱 만들어줘"

# 기능 개발용 Autopilot
omx "autopilot: 사용자 대시보드 구현해줘"

# 병렬 리팩토링
omx "ulw: userId를 user_id로 전부 변경해줘"

# 지속적 디버깅
omx "ralph: 모든 TypeScript 에러 고쳐줘"

# 토큰 효율적 빠른 수정
omx "eco: gitignore에 .env 추가해줘"

# 실행 없이 계획만
omx "plan: 결제 시스템 설계하자"
```

## 스킬 (31개)

### 오케스트레이션
| 스킬 | 설명 |
|------|------|
| `team` | 멀티에이전트 단계별 파이프라인 |
| `autopilot` | 자율 실행 |
| `ultrawork` | 병렬 실행 |
| `ultrapilot` | 최대 병렬화 |
| `ralph` | 지속 모드 |
| `pipeline` | 순차 처리 |
| `swarm` | 레거시 멀티에이전트 (→ team) |

### 계획 & 분석
| 스킬 | 설명 |
|------|------|
| `planner` | 인터뷰 기반 계획 |
| `ralplan` | 반복적 계획 합의 |
| `analyze` | 코드 품질 분석 |
| `research` | 심층 연구 |
| `deepsearch` | 코드베이스 탐색 |

### 개발
| 스킬 | 설명 |
|------|------|
| `eco` | 토큰 효율 모드 |
| `tdd` | 테스트 주도 개발 |
| `build-fix` | 빌드 에러 수정 |
| `deepinit` | 프로젝트 초기화 |
| `release` | 버전 & 체인지로그 |

### 품질 & 리뷰
| 스킬 | 설명 |
|------|------|
| `reviewer` | 코드 리뷰 |
| `code-review` | 종합 리뷰 |
| `security-review` | 보안 감사 |
| `ultraqa` | 병렬 테스팅 |

### 도구 & 유틸리티
| 스킬 | 설명 |
|------|------|
| `git-master` | Git 워크플로우 |
| `playwright` | E2E 테스팅 |
| `debug` | 체계적 디버깅 |
| `mcp-setup` | MCP 설정 |
| `configure-notifications` | 알림 설정 |

### 시스템
| 스킬 | 설명 |
|------|------|
| `doctor` | 설치 진단 |
| `hud` | 실시간 메트릭 |
| `trace` | 실행 트레이싱 |
| `learner` | 패턴 추출 |
| `note` | 세션 노트 |

## 에이전트 (32개)

### 주요 오케스트레이션
- **PM** — 마스터 오케스트레이터
- **Coordinator** — 병렬 실행 관리
- **Executor** — 작업 실행
- **Deep Executor** — 복잡한 구현

### 계획 & 분석
- **Planner** — 실행 가능한 계획 생성
- **Analyst** — 시스템 분석
- **Researcher** — 정보 수집
- **Explorer** — 코드베이스 탐색

### 아키텍처 & 설계
- **Architect** — 시스템 설계
- **Designer** — UI/UX 설계
- **System Designer** — 분산 시스템

### 개발
- **Frontend** — React, Vue, TypeScript
- **Backend** — API, 데이터베이스
- **Fullstack** — 종단간 개발
- **Mobile** — React Native, Flutter
- **DevOps** — CI/CD, 인프라

### 품질 & 테스팅
- **Tester** — 유닛/통합 테스트
- **QA** — 품질 보증
- **Security** — 보안 엔지니어링
- **Performance** — 성능 최적화

### 리뷰 & 비평
- **Reviewer** — 코드 리뷰
- **Critic** — 가정 검증

### 전문 분야
- **Scientist** — 데이터 사이언스
- **Data** — 데이터 엔지니어링
- **ML** — 머신러닝
- **Writer** — 문서화
- **Docs** — API 문서
- **Vision** — 시각적 분석

### 지원
- **Debugger** — 버그 찾기
- **Refactorer** — 코드 개선
- **Migrator** — 업그레이드 & 마이그레이션

## CLI 레퍼런스

```bash
omx "작업 설명"                  # 모드 자동 감지
omx "autopilot: 작업"           # 명시적 모드
omx -m ultrawork "작업"         # 모드 강제
omx --model gpt-4.1 "작업"      # 모델 지정
omx --list                      # 세션 목록
omx --resume <id>               # 세션 재개
omx --status                    # 상태 확인
omx -v "작업"                   # 상세 출력
```

## 크레딧

- [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) — 원본 영감
- [oh-my-opencode](https://github.com/code-yeongyu/oh-my-opencode) — 아키텍처 참조
- [Supabase Agent Skills](https://github.com/supabase/agent-skills) — 스킬 구조
- [Vercel Research](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — 설계 철학

## 라이선스

MIT
