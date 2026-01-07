# HLWComfy v0.8.0 Update & Merge Documentation

## Overview
This repository has been updated to merge upstream **ComfyUI v0.8.0** while preserving critical HLW internal customizations.

## 🔄 Merge Details
- **Base**: Upstream ComfyUI v0.8.0 (Tag: `v0.8.0`)
- **Strategy**: 
  - Core files updated to v0.8.0 defaults.
  - Local customizations preserved via git stash and manual restoration.
  - Conflict resolution prioritized upstream stability for core logic while keeping local hooks and API adaptations.

## ✅ Preserved Customizations

### 1. API & Environment
- **Comfy API**: Restored local custom implementations in `comfy_api/` including `_resources.py`, `_io.py`, and `_ui.py`.
- **Requirements**: Added `comfy-kitchen>=0.2.3` to `requirements.txt`.
- **Code Owners**: Updated `CODEOWNERS` to include `@guill`.

### 2. Core Patches
- **Hook Breaker**: Preserved `hook_breaker_ac10a0.py` to prevent custom nodes from hooking critical functions.
- **CUDA Malloc**: Retained custom version logic in `cuda_malloc.py`.
- **Version**: Bumped `comfyui_version.py` from `0.3.75` to `0.8.0`.

### 3. Model Compatibility
- **Lightricks**: Fixed import errors in `comfy/ldm/lightricks/embeddings_connector.py` by ensuring `model.py` contains required frequency grid functions (`generate_freq_grid_np`, `interleaved_freqs_cis`).

## 🛠 Usage
Run the standard user batch file to start:
```bash
user\HLWUser.bat
```
This ensures all extra model paths (checkpoints, loras, etc.) are loaded correctly from `E:\AI_Model`.

## ⚠️ Known Notes
- If `ModuleNotFoundError: No module named 'comfy_api.latest._resources'` occurs, it indicates incomplete restoration of the `comfy_api` folder. This has been fixed in the current head.
- `requirements.txt` includes updated `comfyui-frontend-package` and `comfyui-workflow-templates`.
