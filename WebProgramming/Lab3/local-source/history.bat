@echo off
setlocal enabledelayedexpansion

echo [history] Sequential search for last working commit...

REM Save original HEAD and branch
for /f %%i in ('git rev-parse HEAD') do set ORIG_HEAD=%%i
for /f %%i in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%i

REM Get the very first commit
for /f %%i in ('git rev-list --max-parents=0 HEAD') do set OLDEST=%%i

set CURRENT=%ORIG_HEAD%
set PREV_BAD=%ORIG_HEAD%
set FOUND=0

:loop
echo [history] Testing commit: !CURRENT!

REM Checkout to CURRENT
git checkout --quiet !CURRENT! 2>nul
if !errorlevel! neq 0 (
    echo [history] Failed to checkout !CURRENT!.
    goto :cleanup
)

REM Try to compile silently; ant returns 0 if success, non-0 if fail
call ant compile-silent >nul 2>&1
if !errorlevel! equ 0 (
    echo [history] SUCCESS: commit !CURRENT! compiles. This is the last working revision.
    set FOUND=1
    goto :done
)

REM Compilation failed: this commit is bad cant use, move to its parent
echo [history] Commit !CURRENT! fails to compile. Moving to parent...
set PREV_BAD=!CURRENT!

for /f %%i in ('git rev-parse !CURRENT!~1 2^>nul') do set PARENT=%%i
if "!PARENT!"=="" (
    echo [history] No parent found. Reached the beginning of history.
    goto :no_working
)
if "!PARENT!"=="!CURRENT!" (
    echo [history] Reached the very first commit (no parent). No working revision exists.
    goto :no_working
)

REM If PARENT is the oldest, this is our last chance
if "!PARENT!"=="%OLDEST%" (
    echo [history] At the first commit. Testing it one more time...
)

set CURRENT=!PARENT!
goto :loop

:done
REM Generate diff: changes introduced in the FIRST BROKEN commit
REM CURRENT = last working commit, PREV_BAD = first broken commit after it
echo [history] Generating diff: !CURRENT! (last working) -^> !PREV_BAD! (first broken)
git diff !CURRENT! !PREV_BAD! > broken_diff.diff
echo [history] Diff saved to broken_diff.diff.
goto :cleanup

:no_working
echo [history] No working revision found in the entire history.

:cleanup
REM Return to original branch
git checkout --quiet %BRANCH% 2>nul
echo [history] Returned to branch %BRANCH%.
echo [history] Search complete.
