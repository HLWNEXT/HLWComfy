---
name: next-comfy-update
description: Manage upstream updates for NEXT comfy, the user's private, locally-customized fork of ComfyUI. Use this skill whenever the user wants to update ComfyUI, pull/sync from upstream, get the latest ComfyUI release, resolve merge conflicts in their comfy fork, or merge an update branch back to main. Trigger on any mention of "NEXT comfy", "update comfy", "upstream pull", "new ComfyUI release", or conflicts between local ComfyUI modifications and upstream changes.
---

# NEXT Comfy Upstream Update

NEXT comfy is a private fork of [ComfyUI](https://github.com/comfyanonymous/ComfyUI) carrying local modifications. Upstream moves fast, so periodic syncs are needed — but because of the local changes, merge conflicts are *expected and normal*. The whole strategy of this skill is isolation: **all upstream merging happens on a dedicated update branch, never directly on main.** Main stays working at all times; if an update goes sideways, the branch is simply deleted and nothing is lost.

The workflow: preflight checks → pick the target release → create update branch → merge & resolve conflicts → user review + smoke test → merge to main.

## Phase 0 — Preflight

Before touching anything, establish a safe starting point:

1. Locate the repo. If the path isn't known from context or memory, ask the user (and remember it for next time if a memory system is available).
2. Working tree must be clean. Run `git status --porcelain`. If there are uncommitted changes, stop and ask the user whether to commit or stash them — never proceed with a dirty tree, because a failed merge could tangle their in-progress work.
3. Check out `main` (or the repo's primary branch) and make sure it's current with `origin` (`git pull --ff-only origin main`). If the pull isn't fast-forward, stop and sort that out with the user first.
4. Verify remotes with `git remote -v`:
   - `origin` → the private NEXT comfy repo
   - `upstream` → the original ComfyUI repo. If missing, add it: `git remote add upstream https://github.com/comfyanonymous/ComfyUI.git`
5. Fetch upstream including tags: `git fetch upstream --tags`

## Phase 1 — Pick the target release

Target the **latest official release tag**, not the tip of upstream master (releases are more stable):

```bash
# newest upstream release
git tag -l 'v*' --sort=-version:refname | head -5
# release currently incorporated in main
git tag -l 'v*' --merged main --sort=-version:refname | head -1
```

If main is already at the latest tag, report that and stop — nothing to do.

Otherwise, give the user a preview before committing to the update:

- How far behind: `git log --oneline <current>..<target> | wc -l` commits, plus notable changes (`git log --oneline <current>..<target> | head -20`).
- **Predicted conflicts** — this is the valuable part. Intersect the files the fork has modified with the files upstream touched:

```bash
comm -12 \
  <(git diff --name-only $(git merge-base main <current>) main | sort) \
  <(git diff --name-only <current> <target> | sort)
```

Files in both lists are likely conflict sites. Show them to the user and confirm before proceeding. If the user wants a different tag (e.g. skipping a known-bad release), use that instead.

## Phase 2 — Create the update branch

```bash
git checkout -b update/<target-tag> main    # e.g. update/v0.3.44
```

Never run the merge on main itself. The branch is the blast containment: conflicts, mistakes, and broken states all live here until proven good.

## Phase 3 — Merge and resolve conflicts

```bash
git merge <target-tag>
```

Conflicts are expected. For each conflicted file, the guiding principle is: **adopt upstream's improvements while preserving the intent of the local modification.** Concretely:

- Read both sides plus the merge base (`git show :1:<file>`, `:2:` ours, `:3:` theirs) to understand *why* each side changed the code — don't just pattern-match on the markers.
- If a `LOCAL_CHANGES.md` (or similar) exists in the repo root, read it first — it documents what the local modifications are for and is the best guide to which side's intent must survive.
- Orthogonal changes (local mod and upstream change touch the same lines but do different jobs): combine both.
- Upstream refactored code that a local mod lives in: port the local mod onto the new structure rather than keeping the old structure.
- Upstream fixed a bug in code the fork also patched: prefer upstream's fix, re-apply the local delta on top if it's still needed.
- Genuinely unclear whose behavior should win: keep local behavior, and flag the file prominently in the summary for the user to rule on.

Keep a running **resolution log** as you go — one entry per file: what conflicted, what was decided, and why. Commit the merge with this log in the commit body.

Also glance at `requirements.txt` in the merge diff; if upstream added or bumped dependencies, note it — the smoke test will fail with ImportErrors otherwise, and the user's environment will need `pip install -r requirements.txt`.

## Phase 4 — Review and smoke test

1. Present the resolution log to the user as a compact summary: files conflicted, decision per file, and any flagged judgment calls.
2. Smoke test — confirm ComfyUI actually starts on the update branch:

```bash
timeout 90 python main.py --cpu 2>&1 | tee /tmp/comfy_smoke.log
```

   (Use the user's normal launch command if they have one.) Success = the server logs that it's listening (e.g. "Starting server" / "To see the GUI go to") with no tracebacks during startup. Kill it once startup is confirmed. If it fails, fix on the branch and re-test — main is still untouched.

3. **Wait for explicit user approval before merging to main.** This is their call, not the skill's.

## Phase 5 — Merge to main

Only after approval:

```bash
git checkout main
git merge --no-ff update/<target-tag>   # keep the update visible in history
git push origin main
git branch -d update/<target-tag>       # merge commit preserves everything
```

If local customizations were relocated or reworked during conflict resolution, offer to update `LOCAL_CHANGES.md` to match — keeping it accurate makes the *next* update's conflicts much easier.

## If things go wrong

Main is never at risk in this workflow, so recovery is always cheap:

- Mid-merge mess on the branch: `git merge --abort` and retry.
- Branch is unsalvageable: `git checkout main && git branch -D update/<tag>` — clean slate, start over.
- Problem discovered *after* merging to main: `git revert -m 1 <merge-commit>` reverts the whole update in one commit, or re-open a fix branch from main.
- An update stalls (conflicts too hairy to finish today): leave the branch as-is; it can be resumed any time. Note the state so the next session picks it up.
