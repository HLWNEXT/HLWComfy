---
description: How to safely update the HLWComfy core while keeping local modifications.
---
# Workflow: Update ComfyUI & Resolve Conflicts

This workflow updates the HLWComfy core by pulling from the public upstream ComfyUI repository while preserving customized files and keeping the private HLWComfy repository in sync.
**CRITICAL**: The update process is strictly one-directional (upstream -> local -> origin). NEVER push to `upstream`. If fetching/pushing to `origin` fails with an authentication error, the GitHub Personal Access Token may have expired (needs renewal every 3 months).

1. Verify the current git status to ensure there are no uncommitted changes (`git status`). Stash or commit any changes if necessary.
2. Ensure the local branch is in sync with the private remote `origin` master:
   `git checkout master`
   `git pull origin master`
3. Determine the target ComfyUI version or commit, and create a dedicated branch for the update:
   `git checkout -b update/vX.Y.Z` or `git checkout -b update/latest`
// turbo
4. Add the public upstream remote if it doesn't exist and safely fetch updates, preventing accidental pushes:
   `git remote add upstream https://github.com/comfyanonymous/ComfyUI.git`
   `git remote set-url --push upstream no_push`
   `git fetch upstream`
5. Rebase or merge the upstream changes into the new update branch:
   `git pull --rebase upstream master`
6. If conflicts occur (e.g., in `execution.py` or `nodes.py`), open the conflicted files and resolve them by preserving the HLW modifications over the default upstream code. Commit the resolved conflicts.
7. Re-install any new requirements from the updated core:
   `pip install -r requirements.txt`
8. Run a local test to verify ComfyUI starts and operates without errors.
9. **Human Review**: Wait for the user to approve the successful test.
10. Upon user approval, checkout to the main branch, merge the update branch, delete the update branch, and sync with the private `origin` repository:
    `git checkout master`
    `git merge update/<branch-name>`
    `git branch -d update/<branch-name>`
    `git push origin master`
