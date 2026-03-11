---
trigger: model_decision
description: Apply this rule when starting or modifying a web-based rapid prototype, specifically when managing Conda environments, performing browser-led testing.
---

## 1. Documentation & Code Style
*   **Explain "Why"**: Every file must include a header comment explaining what the code does in plain English.
*   **Line-by-Line Annotations**: For complex logic, add comments on the same line to explain the "how" for a beginner.
*   **Modular Design**: 
    *   `main.py` is only for the entry point.
    *   Store business logic in separate, descriptive files (e.g., `api_handler.py`, `ui_utils.py`).
*   **Lightweight & Modern**: Prefer standard libraries or modern, minimal frameworks (e.g., FastAPI, Streamlit).

## 2. Environment Management (Conda)
*   **Conda Only**: You MUST use `conda` for environment management. Never use `venv` or global Python.
*   **Lifecycle**: 
    1. Create environment: `conda create -n project_name python=3.10`
    2. Activate: `conda activate project_name`.
    3. Export dependencies: Always maintain an `environment.yml` file.

## 3. Browser Demo & Safety
*   **Pre-Launch Approval**: Before starting any browser-based demo or local server, you must ask the user: "Ready to launch the browser demo?".
*   **Verification Steps**: 
    *   During the demo, use the browser agent to navigate.
    *   **Crucial**: You MUST take a screenshot of each successful step and any errors encountered.
    *   Save these images in a `/demo_logs/` folder with descriptive names.

## 4. Version Control (Git)
*   **Branching Strategy**: Create a new branch for every distinct feature or fix (e.g., `feat-add-login`).
*   **Commits**: Use descriptive commit messages following the "Conventional Commits" style (e.g., `feat: added conda environment file`).
*   **Review**: After finishing a task, provide a summary of the `git diff` to the user.