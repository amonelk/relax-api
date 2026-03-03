---
name: api-docs-by-services
description: Generate bilingual API documentation files from service names under relax-api/services. Use when producing tool API docs, writing service API docs, or when the user asks to create service-based .md docs in the repository root.
---

# API Docs By Services

## Purpose

Generate API documentation in both Chinese and English based on each first-level service directory under `services`, and place docs in the repository root.

## When To Use

Apply this skill when the request includes any of these intents:

- Produce tool API docs for this project
- Create API docs from `services` directory names
- Generate bilingual documentation (Chinese + English)
- Batch-create root-level markdown docs for each service

## Required Output Rule

For every first-level directory in `services`, create two files in the repository root:

- `{service}.zh.md`
- `{service}.en.md`

Example:

- `services/markitdown` -> `markitdown.zh.md` and `markitdown.en.md`

Do not create docs for:

- Non-directory entries in `services`
- Vendor/upstream nested directories
- Existing hidden/system folders

## Workflow

Use this checklist:

```text
Task Progress:
- [ ] Step 1: Discover first-level service names
- [ ] Step 2: Collect each service API surface
- [ ] Step 3: Generate Chinese docs
- [ ] Step 4: Generate English docs
- [ ] Step 5: Validate naming and location
```

### Step 1: Discover service names

Only use first-level directories directly under `services`.

### Step 2: Collect API surface

For each service, read minimal relevant source files and extract:

- Capability summary
- Input parameters and constraints
- Output format and fields
- Error handling and status behavior
- Usage examples

If service details are unclear, document known behavior first and mark unknown sections as TODO.

### Step 3: Write Chinese doc (`{service}.zh.md`)

Use this structure:

```markdown
# {service} API 文档

## 1. 概述
## 2. 接口列表
## 3. 请求参数
## 4. 返回结构
## 5. 错误处理
## 6. 示例
## 7. 限制与注意事项
```

### Step 4: Write English doc (`{service}.en.md`)

Mirror Chinese content semantically, with this structure:

```markdown
# {service} API Documentation

## 1. Overview
## 2. Endpoints
## 3. Request Parameters
## 4. Response Schema
## 5. Error Handling
## 6. Examples
## 7. Limits and Notes
```

### Step 5: Validate

Before finishing, verify:

- Files are created in repo root (not inside `services`)
- Naming matches exactly `{service}.zh.md` and `{service}.en.md`
- Chinese and English docs are both present for each service
- Content reflects actual codebase behavior, not guessed APIs

## Style Constraints

- Keep docs simple and deployment-focused
- Prefer practical examples over long theory
- Keep terminology consistent across languages
- Avoid exposing internal secrets or sensitive implementation details
- **Do not include local/development information**: no `localhost`, `127.0.0.1`, internal port numbers, local file paths, or internal implementation details (service directories, internal function names)
- Use the production service base URL in all examples: `https://relax-api.onrender.com`
- Overview section should describe user-facing behavior only, not internal code structure

