# SupportPilot

SupportPilot 是一个面向企业客户支持场景的 AI Agent 作品集项目。它计划帮助支持团队更快地理解客户问题、查找信息并生成合适的回复。

## 目标用户

- 企业客服团队
- 客户支持专员
- 客户成功经理
- 希望了解客户支持状态的团队管理者

## 主要产品目标

构建一个可靠、可评估、能够与人工客服协作的企业客户支持 AI Agent，从而提升问题处理效率和回复质量。

## 计划中的能力

- **Agent**：理解客户问题并组织处理步骤。
- **Tool Calling**：调用知识库或其他业务工具获取信息。
- **RAG**：从企业文档和知识库中检索相关内容。
- **Human-in-the-loop**：在需要时交由人工审核或接管。
- **Evaluation**：评估回答的准确性、相关性和安全性。

## 当前状态

项目目前处于环境设置和项目初始化阶段，暂未实现 Agent 或业务功能。

## Python 环境

项目使用 Python 3.12。安装当前依赖：

```bash
pip install -r requirements.txt
```

开发时请根据 `.env.example` 创建本地 `.env` 文件，并填写自己的 API key。不要把真实密钥提交到代码仓库。

## Current Capabilities

- Multi-turn terminal conversation
- DeepSeek model via OpenAI-compatible API
- Order lookup
- Ticket creation
- Ticket status lookup
- Ticket status update
- SQLite business data
- Tool input validation
- Basic conversation history limit

## RAG Knowledge Base

SupportPilot currently supports retrieval-augmented generation for enterprise policy questions.

Knowledge base topics include:

- Return and exchange policy
- Shipping policy
- Membership policy
- Refund policy

RAG pipeline:

```text
User Query
    ↓
Knowledge Base Tool
    ↓
Retriever
    ↓
BGE Chinese Embedding
    ↓
ChromaDB
    ↓
Relevant Chunks
    ↓
SupportPilot Agent
    ↓
Answer with source citation


---

# 7）更新项目结构

```text
supportpilot-agent/
├── run.py
├── data/
│   └── knowledge/
├── evals/
│   ├── rag_cases.jsonl
│   ├── run_rag_eval.py
│   ├── workflow_cases.jsonl
│   ├── run_workflow_eval.py
│   ├── hitl_cases.jsonl
│   └── run_hitl_eval.py
├── src/
│   └── supportpilot/
│       ├── agent.py
│       ├── config.py
│       ├── db.py
│       ├── rag/
│       ├── tools/
│       │   ├── kb_tools.py
│       │   ├── order_tools.py
│       │   └── ticket_tools.py
│       └── workflows/
│           └── shipping_workflow.py
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
└── requirements.txt

Current embedding model:
BAAI/bge-small-zh-v1.5

Current retrieval threshold:
MAX_DISTANCE = 0.7


---
M6 架构
```markdown
## Safety Architecture

```text
                    ┌──────────────┐
                    │     User     │
                    └──────┬───────┘
                           ↓
                    ┌──────────────┐
                    │    Agent     │
                    └──────┬───────┘
                           ↓
                 ┌───────────────────┐
                 │ Read or Write?    │
                 └────────┬──────────┘
                          │
              ┌───────────┴───────────┐
              ↓                       ↓
        Read Operation          Write Operation
              ↓                       ↓
       Execute Directly         Approval Required
                                      ↓
                                Human Review
                               ┌──────┴──────┐
                               ↓             ↓
                            Approve        Reject
                               ↓             ↓
                         Database Write    No Write


```markdown
## RAG Evaluation

A small baseline evaluation set is used to validate retrieval quality.

Current baseline results:

| Metric | Result |
|---|---:|
| Top1 Accuracy | 100% (4/4) |
| Recall@3 | 100% (4/4) |
| No-answer Accuracy | 100% (1/1) |

These results are based on a small smoke-test dataset and should not be interpreted as production-level accuracy.

Evaluation cases currently cover:

- Refund timing
- Return eligibility
- Shipping timing
- Membership benefits
- Out-of-domain / no-answer questions

## Evaluation System

SupportPilot includes a multi-layer evaluation system covering retrieval quality, workflow correctness, HITL safety, Agent tool selection, and intent routing.

Current evaluation suites:

- RAG Eval
- Workflow Eval
- HITL Eval
- Agent Tool Calling Eval
- Intent Route Eval

All suites can be executed through a single command:

```bash
python evals/run_all_evals.py


继续追加：

```markdown
## Quality Gates

Each evaluation suite has an explicit regression quality gate.

Current smoke-test gates:

| Eval Suite | Quality Gate |
|---|---|
| RAG Eval | Top1 Accuracy = 100%, Recall@3 = 100%, No-answer Accuracy = 100% |
| Workflow Eval | Accuracy = 100% |
| HITL Eval | Accuracy = 100% |
| Agent Tool Eval | Accuracy = 100% |
| Intent Route Eval | Accuracy = 100% |

These strict thresholds are used as regression gates for the current small controlled test set. They should not be interpreted as production-level performance guarantees.

## Failure Case Tracking

Failed evaluation cases are automatically recorded in:

```text
data/logs/eval_failures.jsonl

## RAG Optimization Notes

The first RAG prototype used ChromaDB's default embedding model.

Baseline result:

- Top1 Accuracy: 75%
- Recall@3: 100%
- No-answer Accuracy: 100%

```markdown
## Regression History

Every full evaluation run records a regression summary in:


然后加入自动报告：

```markdown
## Evaluation Report

Each unified evaluation run automatically generates:

```text
evals/eval_report.md


再加 Release Gate：

```markdown
## Release Gate

SupportPilot includes a project-level release gate.

The current version is marked:

```text
READY


再加一个总架构图：

```markdown
## Evaluation Architecture

```text
Test Cases
    ↓
Individual Eval Suites
    ├─ RAG Eval
    ├─ Workflow Eval
    ├─ HITL Eval
    ├─ Agent Tool Eval
    └─ Intent Route Eval
    ↓
Suite Quality Gates
    ↓
Unified Eval Runner
    ↓
Overall Regression
    ├─ Failure Case Log
    ├─ Regression History
    └─ eval_report.md
    ↓
Release Gate
    ├─ READY
    └─ NOT READY

```text
data/logs/eval_regression.jsonl

Several retrieval improvements were tested:

1. Fixed-size character chunking
2. Paragraph-based chunking
3. Title + paragraph chunking
4. Chinese embedding model replacement
5. Similarity threshold calibration

After switching to:

```text
BAAI/bge-small-zh-v1.5

## Shipping Exception Workflow

SupportPilot includes a deterministic workflow for handling shipping-delay cases.

Workflow:

```text
User / Agent Trigger
        ↓
Check Order
        ↓
Retrieve Shipping Policy
        ↓
Evaluate Shipping Delay
        ↓
Is Overdue?
   ├─ No → Finish
   └─ Yes
        ↓
Check Existing Open Ticket
        ↓
Existing Ticket?
   ├─ Yes → Reuse Ticket
   └─ No  → Create Ticket

## Human-in-the-loop Approval

SupportPilot adds human approval gates for write operations.

Read-only operations can execute directly:

- Query order status
- Query ticket status
- Retrieve enterprise knowledge

Write operations require explicit human approval:

- Create support ticket
- Update ticket status
- Create shipping-delay ticket from workflow

Approval flow:

```text
User Request
    ↓
Agent / Workflow
    ↓
Write Operation Detected
    ↓
Approval Required
    ↓
Human Decision
   ├─ approve → Execute Write
   └─ reject  → Stop Without Write

## Approval Audit Log

Human approval decisions are persisted locally as JSONL:

```text
data/logs/approval_log.jsonl





