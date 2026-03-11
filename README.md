# HLW Internal FOR R&D Comfy Hub

Custom ComfyUI fork with API node integration and environment variable support.

## Features

### COMFY_API_KEY Environment Variable Integration

All API nodes in the `comfy_api_nodes` directory now automatically use the `COMFY_API_KEY` environment variable for authentication. This eliminates the need to configure API keys individually for each node.

#### Setup

The `COMFY_API_KEY` is configured in `user/HLWUser.bat`:

```batch
set COMFY_API_KEY=comfyui-afb307d0765bbae8c3f6e28cff7e1ce5fdfff1c9a67a0f09c05d409c09fab7c3
```

#### How It Works

**Authentication Priority Order:**
1. Bearer token from `IO.Hidden.auth_token_comfy_org` (highest priority)
2. **`COMFY_API_KEY` environment variable** (automatic)
3. API key from `IO.Hidden.api_key_comfy_org` (fallback)

**Implementation:**
- Modified `comfy_api_nodes/util/_helpers.py` → `get_auth_header()` function
- Automatically applies to all 26 API nodes without individual modifications
- Fully backward compatible with existing workflows

**Supported API Nodes:**
- Gemini (nodes_gemini.py)
- OpenAI (nodes_openai.py)
- Stability AI (nodes_stability.py)
- And 23 other API providers

#### Usage

1. Start ComfyUI using `user/HLWUser.bat` (sets the environment variable)
2. Load any workflow with API nodes
3. API authentication happens automatically - no manual configuration needed

### Quantized Model Support

This installation includes **`comfy_kitchen`** (v0.1.0) for loading quantized models like Flux and Qwen.

**Supported Quantization Formats:**
- **FP8** (float8_e4m3fn, float8_e5m2) - 8-bit floating point
- **NVFP4** - 4-bit quantization with block scales

**Benefits:**
- 2-4x reduction in VRAM usage
- Faster inference with tensor core acceleration
- Automatic dequantization during forward pass

**Requirements:**
- CUDA 13.0+ recommended for optimized operations
- Falls back to CPU implementations on older CUDA versions

## Post-Update Import Fix Procedure

After pulling upstream ComfyUI updates, some `comfy_api_nodes` files may fail to import if modules have been renamed or removed. The startup log will show `IMPORT FAILED` and `ModuleNotFoundError` entries. Follow this procedure to resolve them.

### Known Module Relocations

| Old import path | New import path | Affected files |
|---|---|---|
| `comfy_api_nodes.apinode_utils` | `comfy_api_nodes.util` | `nodes_gemini.py`, `nodes_kling.py` |

### How to Fix a `ModuleNotFoundError` After an Update

1. **Identify the failing file** from the startup log (`IMPORT FAILED: nodes_xyz.py`).
2. **Find the bad import** — look for `from comfy_api_nodes.<old_module> import ...`.
3. **Locate where the symbol moved** — check `comfy_api_nodes/util/__init__.py` and its sub-modules (`conversions.py`, `validation_utils.py`, `upload_helpers.py`, `download_helpers.py`).
4. **Update the import** to point at the new location (usually `from comfy_api_nodes.util import ...`).

### Missing Utility Modules (`mapper_utils`, etc.)

If a utility module referenced in a node file no longer exists in the upstream source, create it locally inside `comfy_api_nodes/`. Document it here so it survives future merges.

| File | Purpose | Status |
|---|---|---|
| `comfy_api_nodes/mapper_utils.py` | `model_field_to_node_input()` — maps Pydantic model fields to ComfyUI INPUT_TYPES entries | Created locally; not in upstream |

**`model_field_to_node_input` signature:**
```python
model_field_to_node_input(io_type, model_cls, field_name, enum_type=None, **kwargs)
# Returns (io_type, {tooltip, **kwargs}) or ([enum_values], {tooltip, **kwargs}) for IO.COMBO
```

## Recent Changes

### 2026-03-11: Upgrade to ComfyUI v0.16.4

**Updated:**
- Merged upstream ComfyUI v0.16.4 (branch renamed from `update/v0.16.2` → `update/v0.16.4`, then merged to `master`)
- New Gemini image nodes: **Nano Banana** (`GeminiImage`), **Nano Banana Pro** (`GeminiImage2`), **Nano Banana 2** (`GeminiNanoBanana2`) backed by Gemini 3.x image models
- New **Math Expression** node with simpleeval evaluation
- New **TencentSmartTopology** node
- Gemini LLM model list expanded with Gemini 3.x models (gemini-3-pro-preview, gemini-3-1-pro, gemini-3-1-flash-lite)

**Fixed:**
- `execution.py`: Guard `COMFY_API_KEY` injection to **v1 nodes only** — v3-style `IO.ComfyNode` nodes (`GeminiImage`, etc.) crashed with `unexpected keyword argument 'comfy_api_key'` because they handle auth internally via `sync_op()`. Fix: check `v3_data is None` before injecting. See [Post-Update section](#v3-node-comfy_api_key-injection-guard) below.

### 2026-01-28: COMFY_API_KEY Integration & Bug Fixes

**Added:**
- Environment variable support for API authentication in `comfy_api_nodes/util/_helpers.py`
- Automatic API key injection for all 26 API node providers
- Comprehensive documentation in walkthrough.md
- **`comfy_kitchen` dependency** (v0.1.0) for quantized model support

**Fixed:**
- Removed obsolete API key injection code from `execution.py` (lines 603-632)
- Resolved `NameError: name 'hidden_inputs' is not defined` error
- Cleaned up redundant authentication logic
- **Model loading error** for Flux and Qwen quantized models (`AttributeError: 'NoneType' object has no attribute 'Params'`)

**Technical Details:**
- Single function modification (`get_auth_header()`) applies globally
- No async/sync compatibility issues
- Maintains full backward compatibility
- Installed `comfy_kitchen` enables FP8/NVFP4 quantization support (2-4x memory reduction)


## Project Structure

```
HLWComfy/
├── comfy_api_nodes/          # API node implementations
│   ├── util/
│   │   └── _helpers.py       # Authentication logic (modified)
│   ├── nodes_gemini.py       # Google Gemini API
│   ├── nodes_openai.py       # OpenAI API
│   ├── nodes_stability.py    # Stability AI API
│   └── [23 other API nodes]
├── execution.py              # Execution engine (cleaned up)
├── user/
│   └── HLWUser.bat          # Environment setup script
└── README.md                # This file
```

## Development Notes

### V3 Node `COMFY_API_KEY` Injection Guard

ComfyUI v0.16+ introduces **v3-style nodes** that extend `IO.ComfyNode` (e.g., `GeminiImage`, `GeminiNode`, `GeminiNanoBanana2`). These nodes use the new `define_schema()` / `execute()` pattern and handle API auth **internally** via `sync_op()` — the framework reads their `IO.Hidden.api_key_comfy_org` declaration automatically.

#### The Problem

The local `execution.py` injection block (Krita API integration) injects `comfy_api_key` into **all** nodes marked `API_NODE=True`. When this runs for a v3 node, the kwarg is passed into the v3 dispatch chain (`EXECUTE_NORMALIZED_ASYNC`) which calls `execute()` — which does **not** accept `comfy_api_key` as a parameter:

```
TypeError: GeminiImage.execute() got an unexpected keyword argument 'comfy_api_key'
```

#### The Fix — `execution.py`

Guard the injection with `v3_data is None`. `v3_data` is only set for v3 nodes, so this precisely targets v1 nodes:

```python
# execution.py  — inside _async_map_node_over_list, before the coroutine dispatch

# Only inject for v1 API nodes — v3 nodes (IO.ComfyNode) handle auth internally
if v3_data is None and hasattr(obj, 'API_NODE') and getattr(obj, 'API_NODE', False):
    comfy_api_key = os.getenv('COMFY_API_KEY')
    if comfy_api_key:
        inputs = dict(inputs)
        if inputs.get('comfy_api_key') is None:
            inputs['comfy_api_key'] = comfy_api_key
```

**Apply this fix every time upstream updates introduce new v3 API nodes** and the injection block causes `unexpected keyword argument` errors.

#### How to detect v3 vs v1 nodes

| Trait | v1 node | v3 node |
|---|---|---|
| Base class | `ComfyNodeABC` | `IO.ComfyNode` |
| Schema | `INPUT_TYPES()` classmethod | `define_schema()` classmethod |
| Execution | `FUNCTION = "api_call"`, `api_call(self, ...)` | `async def execute(cls, ...)` |
| Auth wiring | `"hidden": {"comfy_api_key": "API_KEY_COMFY_ORG"}` | `IO.Hidden.api_key_comfy_org` in `define_schema` |

### API Authentication Architecture

The authentication system uses a centralized approach:

1. **Request Layer**: API nodes call `sync_op()` or `poll_op()` from `util/client.py`
2. **Authentication Layer**: These functions call `get_auth_header()` from `util/_helpers.py`
3. **Environment Layer**: `get_auth_header()` reads `COMFY_API_KEY` from environment
4. **Header Injection**: API key is automatically added to HTTP request headers

This design ensures:
- Single source of truth for API authentication
- No need to modify individual node files
- Easy to maintain and update
- Proper separation of concerns

### Async/Sync Handling

Both `sync_op()` and `poll_op()` are async functions. The `os.environ.get()` call in `get_auth_header()` is synchronous but safe to use within async contexts, following Python async best practices.

## License

Internal R&D project for HLW.

