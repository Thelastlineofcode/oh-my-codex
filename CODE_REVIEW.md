# Oh My Codex - Code Review

> 리뷰 일시: 2026-02-13
> 리뷰어: 비서

## 📊 요약

| 항목 | 점수 | 비고 |
|------|------|------|
| 아키텍처 | ⭐⭐⭐⭐ | AGENTS.md-first 철학 잘 구현 |
| 코드 품질 | ⭐⭐⭐ | 중복 코드, 일부 개선 필요 |
| 보안 | ⭐⭐⭐ | 기본적 처리, 강화 필요 |
| 테스트 | ⭐⭐ | 테스트 코드 없음 |
| 문서화 | ⭐⭐⭐⭐ | README, 주석 양호 |

**전체 평가**: Approve with suggestions

---

## 🔴 Critical Issues

### 1. 중복 MODE_KEYWORDS 정의
**위치**: `constants.py` vs `router.py`

```python
# constants.py
MODE_KEYWORDS: Dict[str, str] = {
    "autopilot:": "autopilot",
    ...
}

# router.py  
MODE_KEYWORDS = {
    "autopilot": ["autopilot", "auto", "autonomous"],
    ...
}
```

**문제**: 두 파일에서 다른 형식으로 같은 개념을 정의. 동기화 오류 발생 가능.

**수정안**:
```python
# constants.py만 사용, router.py에서 import
from .constants import MODE_KEYWORDS
```

### 2. 하드코딩된 모델명
**위치**: `router.py`, `constants.py`, `agents/base.py`

```python
class ModelTier(Enum):
    FAST = "gpt-4.1-mini"
    STANDARD = "gpt-4.1"
    POWERFUL = "o3"
```

**문제**: 모델명이 여러 곳에 하드코딩. OpenAI 모델 업데이트 시 전체 수정 필요.

**수정안**: `config.toml`에서 로드하도록 변경
```toml
[models]
fast = "gpt-4.1-mini"
standard = "gpt-4.1"
powerful = "o3"
```

---

## 🟠 Major Issues

### 3. 에이전트 캐싱 메모리 누수 가능성
**위치**: `main.py` line 46-71

```python
async def _create_agent(self, role: AgentRole, mcp_servers: List = None) -> "Agent":
    if role in self._agents:
        return self._agents[role]
    # ... 생성 후 캐시
    self._agents[role] = agent
```

**문제**: 
- `mcp_servers`가 달라도 캐시된 에이전트 반환
- 장기 실행 시 메모리 누수

**수정안**:
```python
def _get_cache_key(self, role: AgentRole, mcp_servers: List) -> str:
    servers_hash = hash(tuple(id(s) for s in (mcp_servers or [])))
    return f"{role.value}_{servers_hash}"

async def _create_agent(self, role: AgentRole, mcp_servers: List = None) -> "Agent":
    cache_key = self._get_cache_key(role, mcp_servers)
    if cache_key in self._agents:
        return self._agents[cache_key]
```

### 4. 세션 파일 경쟁 조건
**위치**: `session.py`

```python
def save(self, session: Session) -> None:
    path = self._get_session_path(session.id)
    with open(path, "w") as f:
        json.dump(session.to_dict(), f, indent=2)
```

**문제**: 동시 실행 시 파일 손상 가능

**수정안**:
```python
import tempfile
import shutil

def save(self, session: Session) -> None:
    path = self._get_session_path(session.id)
    # Atomic write
    fd, tmp_path = tempfile.mkstemp(dir=self.base_dir)
    try:
        with os.fdopen(fd, 'w') as f:
            json.dump(session.to_dict(), f, indent=2)
        shutil.move(tmp_path, path)
    except:
        os.unlink(tmp_path)
        raise
```

### 5. 에러 처리 불충분
**위치**: `cli.py` `run_codex_direct()`

```python
except FileNotFoundError:
    print("❌ Codex CLI not found. Install: npm install -g @openai/codex")
    sys.exit(1)
```

**문제**: 
- 다른 에러(권한, 네트워크)는 그냥 crash
- exit code가 항상 1

**수정안**:
```python
except FileNotFoundError:
    print("❌ Codex CLI not found.")
    sys.exit(127)  # command not found
except PermissionError:
    print("❌ Permission denied to run Codex CLI")
    sys.exit(126)  # cannot execute
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
```

---

## 🟡 Minor Issues

### 6. Type Hints 불완전
**위치**: 여러 파일

```python
# 현재
def _get_agents_for_mode(self, mode: str) -> List[AgentRole]:

# 권장 (Python 3.9+)
def _get_agents_for_mode(self, mode: str) -> list[AgentRole]:
```

### 7. 매직 넘버
**위치**: `session.py`, `cli.py`

```python
# session.py
task_hash = hashlib.md5(task.encode()).hexdigest()[:8]

# cli.py
for s in sessions[:15]:  # 왜 15?
```

**수정안**: 상수로 분리
```python
SESSION_HASH_LENGTH = 8
SESSION_LIST_LIMIT = 15
```

### 8. 미사용 코드
**위치**: `router.py`

```python
def suggest_skills(task: str) -> list:
    """Suggest relevant skills for a task."""
    # 이 함수는 어디서도 호출되지 않음
```

### 9. 로깅 일관성
**위치**: `main.py`

```python
def log(self, msg: str, level: str = "info"):
    if self.verbose:
        prefix = {"info": "ℹ️", ...}
```

**문제**: 표준 logging 모듈 미사용. 디버깅 어려움.

**수정안**:
```python
import logging
logger = logging.getLogger(__name__)
```

---

## 🔒 보안 고려사항

### 10. 입력 검증 부재
```python
# cli.py
prompt = " ".join(args.prompt)
```
사용자 입력이 shell로 직접 전달됨. 특수문자 이스케이프 필요.

### 11. 세션 ID 예측 가능
```python
session_id = f"{timestamp}_{task_hash}"
```
MD5는 암호학적으로 안전하지 않음. UUID4 권장.

---

## ✅ 잘된 점

1. **AGENTS.md-first 철학 구현** - 컨텍스트에 항상 로드됨
2. **모듈 분리** - 각 모듈 단일 책임
3. **Graceful degradation** - SDK 없어도 동작
4. **비동기 처리** - async/await 적절히 사용
5. **세션 재개 기능** - 장기 작업 지원

---

## 📝 권장 개선 사항

### 우선순위 높음
- [ ] MODE_KEYWORDS 중복 제거
- [ ] 모델명 설정 파일로 분리
- [ ] 세션 파일 atomic write
- [ ] 테스트 코드 추가

### 우선순위 중간
- [ ] 에이전트 캐시 키 개선
- [ ] 표준 logging 모듈 사용
- [ ] 에러 처리 강화

### 우선순위 낮음
- [ ] Type hints 완성
- [ ] 매직 넘버 상수화
- [ ] 미사용 코드 정리

---

## 🧪 테스트 권장 사항

```
tests/
├── test_router.py      # 복잡도 분류, 모드 감지
├── test_session.py     # CRUD, 동시성
├── test_orchestrator.py # 모드별 에이전트 선택
└── test_cli.py         # CLI 파싱
```

---

**결론**: 전반적으로 잘 설계된 프로젝트. 위 개선사항 반영 시 프로덕션 레벨 도달 가능.
