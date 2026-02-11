@echo off
REM start_step.bat — Zero-friction session start for the fiction pipeline.
REM Displays current pipeline state and context manifest.
REM Usage: scripts\start_step.bat

setlocal

set ROOT=%~dp0..
set STATE=%ROOT%\.pipeline-state.yaml
set VENV=%ROOT%\.venv\Scripts\python.exe

if not exist "%STATE%" (
    echo ERROR: .pipeline-state.yaml not found at %STATE%
    exit /b 1
)

if not exist "%VENV%" (
    echo ERROR: Virtual environment not found. Run: uv venv .venv ^&^& uv pip install -e ".[dev]"
    exit /b 1
)

echo === Fiction Pipeline — Session Start ===
echo.
"%VENV%" "%ROOT%\scripts\context_loader.py" --state "%STATE%" --root "%ROOT%"

endlocal
