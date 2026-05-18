# Sabrina — Reviewing Student Pull Requests

How to handle pull requests from Christine and Floyd. This is a companion to `SABRINA_QUICKSTART.md`. Use this when a student tells you they pushed a branch and opened a PR.

Repo PR list: `https://github.com/perrymlab/blindspot-summer-2026/pulls`

## 1. When a student opens a PR

You will see it in the PR list with an open green dot. GitHub also emails you because you are the only reviewer with write access. Open the PR.

### 1a. What to look at first

On the PR page:

- **Conversation** tab: title, description, any notes the student wrote.
- **Files changed** tab: the actual diff. This is where the review happens.
- **Checks** section at the bottom of Conversation: the `Python tests` workflow. It should be green before you merge.

If `Python tests` is red, do not merge. Click the failed check, copy the relevant error, and either fix it yourself in a follow-up commit on their branch or ask the student to fix and push again.

### 1b. Reviewing the diff

In **Files changed**:

- Hover any line and click the blue `+` icon to add a comment on that exact line.
- Type your comment, click **Start a review** (first comment) or **Add review comment** (subsequent comments). Comments are held until you submit the review, so the student sees them all at once.
- When done, click the green **Review changes** button at the top right.

You get three review choices:

- **Comment**: leaves notes but does not approve or block. Use this for "looks fine, one question" style reviews.
- **Approve**: marks the PR as approved. Combined with green CI, the merge button unlocks.
- **Request changes**: marks the PR as blocked. The student must push more commits before you can approve.

Click the choice and **Submit review**.

## 2. The three outcomes

### 2a. Approve and merge

After you approve and CI is green:

1. Go back to the **Conversation** tab.
2. Click the green **Squash and merge** button.
3. Confirm. The squash commit message defaults to the PR title — adjust if you want.
4. GitHub auto-deletes the student's branch on the remote.

The student then needs to sync locally (see section 3).

### 2b. Request changes

Submit your review with **Request changes** and clear, line-level comments saying exactly what to fix. The student edits the same branch, commits, and pushes again. The PR updates automatically. You will get a re-review request from them.

When their fix looks good, submit a new review with **Approve**, then **Squash and merge** as in 2a.

### 2c. Close without merging

Use this when the work should not go in at all (wrong direction, redundant with someone else's work, abandoned task).

1. Scroll to the bottom of the **Conversation** tab.
2. Click **Close pull request**.
3. Optionally leave a comment explaining why so the student knows.

GitHub does **not** auto-delete the branch when you close without merging — it just closes the PR. The branch sits on the remote until someone deletes it. You can delete it manually:

`https://github.com/perrymlab/blindspot-summer-2026/branches` → trash icon next to the closed branch.

Or from your local clone:

```bash
git push origin --delete <branch-name>
```

## 3. What the student must do after each outcome

You can paste any of these into a comment so the student knows what to run.

### After 2a (merged)

```bash
git checkout main
git pull
git branch -d <their-branch-name>
```

Next task starts from a fresh branch off updated `main`.

### After 2b (changes requested)

Student stays on the same branch:

```bash
git checkout <their-branch-name>
# edit the file based on review comments
git add <changed-files>
git commit -m "Address review feedback"
git push
```

PR updates. Student clicks **Re-request review** in the PR sidebar so you see it's ready again.

### After 2c (closed)

Student drops the branch:

```bash
git checkout main
git pull
git branch -D <their-branch-name>
```

If you already deleted the remote branch, that is enough. If you did not, the student can also run `git push origin --delete <their-branch-name>`.

## 4. Special situations

### 4a. CI failed — should you merge anyway?

No. `Python tests` failing means either the smoke test or pytest broke. Even if the diff looks safe (e.g., a doc-only change), the failure points at something real. Two options:

- Ask the student to investigate and push a fix.
- If you can see it is unrelated to their change (rare), use the **Merge without waiting for requirements to be met (bypass rules)** button. Note in the PR comment that you bypassed CI and why.

Default to asking the student to fix. They learn more that way.

### 4b. PR is "out of date with base branch"

This appears if `main` moved since the student opened the PR. Squash merging usually handles this automatically. If GitHub shows a conflict warning, ask the student to run:

```bash
git checkout <their-branch>
git fetch
git merge origin/main
# resolve conflicts in their editor, then:
git add <resolved-files>
git commit -m "Merge main into branch"
git push
```

Do not have them rebase shared branches — that breaks the PR comment thread.

### 4c. Student edited a folder they should not have

If the diff touches `src/`, `scripts/`, `docs/setup/`, or another student's folder:

- Leave a line comment on the offending file.
- Use **Request changes** and ask them to remove that file from the branch (`git checkout origin/main -- <path>` then commit and push).
- Approve and merge once their branch only touches their own folder again.

### 4d. The patch-N branches reappear

If you ever see `cpage15-patch-N` or `fkdodwell-patch-N` style branches:

- The student used the GitHub web editor instead of editing locally.
- Either complete the merge if the change is good and small, or ask them to redo it from their local clone per the workflow in their quickstart.
- Delete the stale patch-N branch afterward.

## 5. Quick reference

| You want to... | Click |
|---|---|
| Add a line comment | blue `+` on the diff line |
| Submit a review | green **Review changes** → Approve / Comment / Request changes |
| Merge | **Squash and merge** on Conversation tab |
| Reject | **Close pull request** on Conversation tab |
| Bypass CI (rare) | **Merge without waiting for requirements** |
| Delete a stale branch | branches page trash icon, or `git push origin --delete <name>` |

If a PR is stuck and the buttons do not behave the way you expect, send Brian the PR link and a screenshot of the merge-status panel.
