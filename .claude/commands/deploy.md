# /deploy

Deploy the current changes to production on Streamlit Community Cloud.

## Steps

1. **Stop local server** — if a Streamlit background process is running, stop it using TaskStop.

2. **Check git status** — run `git status` to see what files have changed.

3. **Stage tracked files** — run `git add -u` to stage all modified tracked files (do not use `git add .` to avoid accidentally including untracked files).

4. **Commit** — if the user provided a message with the command, use it. Otherwise, write a short commit message in Portuguese (BR) summarizing the changes visible in the diff. Use the standard co-author trailer.

5. **Push** — run `git push origin main`.

6. **Confirm** — tell the user the push was successful and that Streamlit Community Cloud will auto-deploy in about a minute.

## Notes
- If there is nothing to commit (clean working tree), tell the user and skip the commit/push.
- Always use `.venv\Scripts\python.exe` for any Python commands if needed.
- All messages to the user must be in Portuguese (BR).
