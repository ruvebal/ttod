---
title: "The propose-a-quote backend endpoint Team 1's form posts to"
seam: accounts
team_number: 5
team_name: "Accounts, Library, Proposals & Public API"
task_number: 3
area: "Accounts, Content"
verb: contribute
layout: default
lang: en
alt_lang_missing: true
---

# Assignment — Team 5, Task 3: The propose-a-quote backend endpoint Team 1's form posts to

**Seam:** accounts · **Team:** 5 · **Task:** 3 of ~10
**Area(s):** Accounts, Content · **Verb served:** contribute

## 1. Curriculum map

This task exercises the **FE II Unit 3** concepts regarding server-side data mutation and API integration, specifically the discipline of translating a client-side intent into a server-side domain operation without duplicating logic. It reinforces the **FE II Unit 5** testing strategy by requiring that the new endpoint be verified against the existing `ttod_core` primitives, ensuring that the "adapter" layer (the HTTP endpoint) does not introduce new failure modes that the core domain logic already handles.

## 2. Worked example, from the real TTOD app

The existing CLI command `proposal create` in `cli.py` (line 276) already performs the exact operation this task requires: it calls `create_proposal` from `ttod_core/proposals.py` (line 251). This task does not build a new proposal engine; it exposes that same function via an HTTP endpoint. The real function signature and behavior are already defined in `ttod_core/proposals.py`; the endpoint’s only job is to parse the incoming JSON body, validate it against the expected schema, and invoke `create_proposal` with the resulting arguments.

## 3. What "done" looks like

**Visible result:** Team 1’s propose form successfully creates a real proposal record when submitted. The student sees a confirmation that the proposal has been queued for review, and the proposal appears in the reviewer’s queue (handled by Task 4).

**What it includes:**
- A new POST endpoint (e.g., `POST /api/v1/proposals`) that accepts a JSON body containing the quote text, source, and optional metadata.
- The endpoint calls `create_proposal` from `ttod_core/proposals.py` directly, reusing 100% of the existing proposal infrastructure.
- The endpoint returns a standard success response (e.g., `201 Created`) with the ID of the newly created proposal.
- The endpoint is guarded by `requireUser` from `src/lib/auth.server.ts` to ensure only authenticated users can submit proposals.

**What has to be done:**
1. Agree on the request shape with Team 1 (the frontend team) to ensure the JSON body matches what their form submits.
2. Create a new Astro API route (e.g., `src/pages/api/proposals.astro` or a server-side route handler) that imports `create_proposal` from `ttod_core/proposals.py`.
3. Implement the endpoint logic: parse the request body, validate it, call `create_proposal`, and return the result.
4. Ensure the endpoint is protected by `requireUser` so that anonymous users cannot submit proposals.
5. Write a unit test that verifies the endpoint calls `create_proposal` with the correct arguments and returns the expected response.

## 4. Success criteria (functional)

- A signed-in student can submit a proposal via the new endpoint and receive a `201 Created` response.
- An anonymous user attempting to submit a proposal receives a `401 Unauthorized` or redirect to login, as enforced by `requireUser`.
- The proposal created via the endpoint is identical in structure and content to one created via the CLI `proposal create` command.
- The endpoint does not write directly to `ttod.yml`; it only creates a proposal record, which is later accepted via `cli.py proposal accept --reviewer-id`.

## 5. Quality criteria (the part that's new)

- **Code organization:** The endpoint logic is isolated in a single, well-named function that can be easily tested and reused. The import of `create_proposal` is explicit and clear, making the dependency on `ttod_core` visible.
- **AI-use/process documentation:** The student documents the decision to reuse `create_proposal` rather than building a new proposal engine, citing the existing CLI command as the precedent. This demonstrates an understanding of the "single source of truth" principle.
- **Test shape:** The unit test mocks `create_proposal` to verify that the endpoint calls it with the correct arguments and handles errors appropriately. This follows the Trophy-not-Pyramid doctrine by focusing on the endpoint’s behavior rather than the internal implementation of `create_proposal`.
- **Accessibility:** The endpoint is a server-side API, so accessibility is primarily a concern for the frontend form (Team 1’s responsibility). However, the student ensures that the error messages returned by the endpoint are clear and actionable, which aids in debugging and user experience.
- **Oral defense:** The student can explain why the endpoint reuses `create_proposal` instead of implementing new logic, referencing the existing CLI command and the principle of avoiding duplication. They can also explain how the endpoint is guarded by `requireUser` to ensure only authenticated users can submit proposals.

## Closing

> "One source of truth. One place to change. One mind at peace."
> — TTOD `arch-013`, *architecture*

`create_proposal` is that one place. The CLI already calls it; this endpoint's only job is to call it too, from a different door. Writing a second implementation "just for the web" would mean two places to change and two chances to drift apart.