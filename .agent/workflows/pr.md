---
description: How to create a feature branch and pull request for clab-ai-orchestrator
---

# PR Workflow for clab-ai-orchestrator

## Steps

// turbo-all

1. Create a feature branch from main:
```bash
cd /Users/nkchan/clab-ai-orchestrator
git checkout main
git pull origin main
git checkout -b feature/<branch-name>
```

2. Make changes and commit:
```bash
git add -A
git commit -m "<type>: <description>"
```
Commit types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

3. Push the feature branch:
```bash
git push -u origin feature/<branch-name>
```

4. Create a pull request:
```bash
gh pr create --title "<type>: <description>" --body "<details>"
```

5. After PR is merged, clean up:
```bash
git checkout main
git pull origin main
git branch -d feature/<branch-name>
```
