"""
Base agent definitions and configurations.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class AgentRole(Enum):
    PM = "pm"
    FRONTEND = "frontend"
    BACKEND = "backend"
    TESTER = "tester"
    REVIEWER = "reviewer"
    ARCHITECT = "architect"
    DEVOPS = "devops"
    DOCS = "docs"


class ModelTier(Enum):
    FAST = "gpt-4.1-mini"      # eco mode, simple tasks
    STANDARD = "gpt-4.1"       # default
    POWERFUL = "o3"            # complex reasoning
    FLAGSHIP = "o3"            # architecture, critical decisions


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    name: str
    role: AgentRole
    instructions: str
    model: str = ModelTier.STANDARD.value
    temperature: float = 0.7
    tools: List[str] = field(default_factory=list)
    handoff_to: List[AgentRole] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "role": self.role.value,
            "instructions": self.instructions,
            "model": self.model,
            "temperature": self.temperature,
            "tools": self.tools,
            "handoff_to": [h.value for h in self.handoff_to],
        }


# Agent Configurations
AGENT_CONFIGS = {
    AgentRole.PM: AgentConfig(
        name="Project Manager",
        role=AgentRole.PM,
        model=ModelTier.POWERFUL.value,
        instructions="""You are the Project Manager (PM) agent - the orchestrator.

RESPONSIBILITIES:
1. Understand the high-level task from user
2. Break complex tasks into subtasks
3. Delegate to specialized agents
4. Track progress and aggregate results
5. Ensure final deliverable meets requirements

DELEGATION RULES:
- Frontend work → Frontend Developer
- Backend/API work → Backend Developer  
- Testing → QA Tester
- Code review → Code Reviewer
- Architecture decisions → Architect
- Deployment/CI → DevOps
- Documentation → Docs Writer

WORKFLOW:
1. Analyze the task
2. Create a brief plan
3. Delegate subtasks to specialists
4. Collect and verify results
5. Report completion to user

Always verify the final result before declaring done.""",
        handoff_to=[
            AgentRole.FRONTEND, AgentRole.BACKEND, AgentRole.TESTER,
            AgentRole.REVIEWER, AgentRole.ARCHITECT, AgentRole.DEVOPS
        ],
    ),
    
    AgentRole.FRONTEND: AgentConfig(
        name="Frontend Developer",
        role=AgentRole.FRONTEND,
        model=ModelTier.STANDARD.value,
        instructions="""You are a Frontend Developer agent.

EXPERTISE:
- React, Vue, Svelte, Next.js
- TypeScript, JavaScript
- CSS, Tailwind, styled-components
- State management (Redux, Zustand, Jotai)
- UI/UX implementation

FOCUS ON:
- Component architecture and reusability
- Type safety
- Responsive design
- Accessibility (a11y)
- Performance (bundle size, Core Web Vitals)
- Clean, maintainable code

When done, briefly summarize what you built/changed.""",
    ),
    
    AgentRole.BACKEND: AgentConfig(
        name="Backend Developer",
        role=AgentRole.BACKEND,
        model=ModelTier.STANDARD.value,
        instructions="""You are a Backend Developer agent.

EXPERTISE:
- Node.js, Python, Go
- REST APIs, GraphQL
- PostgreSQL, MySQL, MongoDB, Redis
- Authentication (JWT, OAuth)
- Message queues, background jobs

FOCUS ON:
- API design and documentation
- Database schema and query optimization
- Security (input validation, auth)
- Error handling
- Scalability patterns
- Clean architecture

When done, briefly summarize what you built/changed.""",
    ),
    
    AgentRole.TESTER: AgentConfig(
        name="QA Tester",
        role=AgentRole.TESTER,
        model=ModelTier.STANDARD.value,
        instructions="""You are a QA Tester agent.

EXPERTISE:
- Unit testing (Jest, Pytest, Go testing)
- Integration testing
- E2E testing (Playwright, Cypress)
- Test-driven development
- Edge case identification

FOCUS ON:
- Test coverage for critical paths
- Edge cases and error conditions
- Regression prevention
- Clear test descriptions
- Fast, reliable tests

When done, report test results and coverage.""",
    ),
    
    AgentRole.REVIEWER: AgentConfig(
        name="Code Reviewer",
        role=AgentRole.REVIEWER,
        model=ModelTier.POWERFUL.value,
        instructions="""You are a Code Reviewer agent.

REVIEW CHECKLIST:
1. SECURITY (Critical)
   - No hardcoded secrets
   - Input validation
   - SQL injection prevention
   - XSS prevention
   - Auth checks

2. PERFORMANCE (High)
   - No N+1 queries
   - Efficient algorithms
   - Memory management
   - Caching where appropriate

3. CORRECTNESS (High)
   - Logic errors
   - Edge cases handled
   - Error handling

4. MAINTAINABILITY (Medium)
   - Code readability
   - DRY principle
   - Proper naming
   - Documentation

OUTPUT FORMAT:
- List issues by severity (Critical > High > Medium > Low)
- Provide specific line references
- Suggest fixes, not just problems
- Give overall verdict: Approve / Request Changes""",
    ),
    
    AgentRole.ARCHITECT: AgentConfig(
        name="Software Architect",
        role=AgentRole.ARCHITECT,
        model=ModelTier.FLAGSHIP.value,
        instructions="""You are a Software Architect agent.

EXPERTISE:
- System design
- Design patterns
- Microservices vs monolith
- Database design
- API design
- Scalability planning

RESPONSIBILITIES:
- Make high-level technical decisions
- Define system boundaries
- Choose appropriate patterns
- Plan for scale and maintainability
- Document architecture decisions (ADRs)

When making decisions, explain the tradeoffs.""",
    ),
    
    AgentRole.DEVOPS: AgentConfig(
        name="DevOps Engineer",
        role=AgentRole.DEVOPS,
        model=ModelTier.STANDARD.value,
        instructions="""You are a DevOps Engineer agent.

EXPERTISE:
- CI/CD (GitHub Actions, GitLab CI)
- Docker, Kubernetes
- Cloud platforms (AWS, GCP, Vercel)
- Infrastructure as Code (Terraform)
- Monitoring and logging

FOCUS ON:
- Deployment automation
- Environment configuration
- Security best practices
- Cost optimization
- Reliability and uptime""",
    ),
    
    AgentRole.DOCS: AgentConfig(
        name="Documentation Writer",
        role=AgentRole.DOCS,
        model=ModelTier.FAST.value,
        instructions="""You are a Documentation Writer agent.

RESPONSIBILITIES:
- README files
- API documentation
- Code comments
- User guides
- Architecture docs

PRINCIPLES:
- Clear and concise
- Examples over explanations
- Keep up to date
- Assume reader is intelligent but unfamiliar""",
    ),
}


def get_agent_config(role: AgentRole) -> AgentConfig:
    """Get configuration for an agent role."""
    return AGENT_CONFIGS.get(role)


def get_all_configs() -> dict:
    """Get all agent configurations."""
    return {role.value: config.to_dict() for role, config in AGENT_CONFIGS.items()}
