# HLWComfy — Codebase Blueprint

> Purpose: A concise technical reference for onboarding a new developer or AI agent to HLWComfy. Covers repo structure, tech stack, system runtime, and the relationships between core components.

---

## 1. What This Repo Is

HLWComfy is a **private fork of [ComfyUI](https://github.com/comfyanonymous/ComfyUI)** (currently tracking v0.16.4) maintained by HLW for internal R&D. It extends the upstream open-source node-graph AI inference platform with:

- **API node cloud authentication** via `COMFY_API_KEY` env var (no manual key entry)
- **Krita AI bridge** injecting API keys into node execution for Krita-based workflows
- **Quantized model support** via `comfy_kitchen` (FP8 / NVFP4)
- Maintenance scripts and agents for safe upstream merging

Upstream: `https://github.com/comfyanonymous/ComfyUI` (fetch-only, no_push)  
Origin: `https://github.com/HLWNEXT/HLWComfy.git`

---

## 2. Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| ML Framework | PyTorch (CUDA / ROCm / MPS) |
| Web Server | `aiohttp` (async, WebSocket + HTTP) |
| Frontend | React SPA served from `web/` (managed by `FrontendManager`) |
| Data Validation | Pydantic v2 (API request/response models) |
| DB Migrations | Alembic + SQLite (`alembic_db/`) |
| Package Manager | pip / uv |
| API Schema | Auto-generated from `filtered-openapi.yaml` via `datamodel-codegen` |
| Testing | pytest (`tests/`, `tests-unit/`) |

---

## 3. Folder Structure

```
HLWComfy/
│
├── main.py                    # Entry point — CLI arg parsing, server startup
├── server.py                  # aiohttp web server, WebSocket hub, REST routes
├── execution.py               # Prompt execution engine (HLW-modified)
├── execution_upstream.py      # Clean upstream copy of execution.py (reference)
├── nodes.py                   # All built-in node class definitions (CLIPTextEncode, etc.)
├── node_helpers.py            # Node utility helpers
├── folder_paths.py            # Global model/path registry
├── protocol.py                # Binary WebSocket event type definitions
├── comfyui_version.py         # Version string ("0.16.4")
│
├── comfy/                     # Core ML engine
│   ├── sd.py                  # Model loading (checkpoints, VAE, CLIP, LoRA)
│   ├── model_management.py    # VRAM state machine, device routing
│   ├── model_patcher.py       # Runtime weight patching (LoRA, hooks, attention patches)
│   ├── samplers.py            # KSampler logic, conditioning, CFG
│   ├── sample.py              # High-level sampling entrypoint
│   ├── memory_management.py   # Low-level VRAM allocation
│   ├── ops.py                 # Custom ops (FP8, cast, etc.)
│   ├── lora.py / lora_convert.py  # LoRA loading & format conversion
│   ├── cli_args.py            # All CLI argument definitions (argparse)
│   ├── comfy_types/           # IO type system (IO, ComfyNodeABC, InputTypeDict)
│   ├── k_diffusion/           # k-diffusion sampler library
│   ├── ldm/                   # Diffusion model implementations (SD, SDXL, Flux, WAN…)
│   ├── text_encoders/         # CLIP, T5, Qwen, Flux, etc. text encoder wrappers
│   ├── supported_models.py    # Model architecture detection registry
│   └── model_detection.py     # Auto-detect model type from checkpoint
│
├── comfy_execution/           # Graph execution engine
│   ├── graph.py               # DynamicPrompt, ExecutionList (DAG traversal)
│   ├── graph_utils.py         # GraphBuilder, ExecutionBlocker, is_link()
│   ├── caching.py             # Node output caches (Basic, LRU, RAM-pressure, Hierarchical)
│   ├── validation.py          # Input type validation before node execution
│   ├── progress.py            # Progress reporting to frontend
│   ├── jobs.py                # /api/jobs status normalization
│   └── utils.py               # CurrentNodeContext, threading helpers
│
├── comfy_api/                 # Node API framework (v3 node system)
│   ├── latest/                # Latest stable API version
│   │   ├── _io.py             # IO type definitions (IO.ComfyNode, IO.String, IO.Image, etc.)
│   │   └── __init__.py        # ComfyAPI_latest class
│   ├── internal/              # Framework internals (do not use from nodes directly)
│   │   └── __init__.py        # _ComfyNodeInternal, make_locked_method_func, etc.
│   ├── version_list.py        # API version registry
│   └── feature_flags.py       # Runtime feature flag checks
│
├── comfy_api_nodes/           # Cloud API node implementations (HLW + upstream)
│   ├── apis/
│   │   └── __init__.py        # Auto-generated Pydantic request/response models
│   ├── util/
│   │   ├── _helpers.py        # get_auth_header() — COMFY_API_KEY injection (HLW)
│   │   ├── client.py          # sync_op() / poll_op() — async HTTP w/ retry & progress
│   │   ├── conversions.py     # Tensor ↔ base64, audio/video encoding
│   │   ├── validation_utils.py# Input validation helpers
│   │   ├── upload_helpers.py  # File upload to api.comfy.org
│   │   └── download_helpers.py# URL → image tensor
│   ├── mapper_utils.py        # model_field_to_node_input() — Pydantic → INPUT_TYPES (HLW-local)
│   ├── nodes_gemini.py        # Google Gemini (LLM + Image nodes; v3-style IO.ComfyNode)
│   ├── nodes_openai.py        # OpenAI GPT/DALL-E
│   ├── nodes_stability.py     # Stability AI
│   ├── nodes_flux.py / nodes_bfl.py  # Black Forest Labs (Flux.1)
│   ├── nodes_kling.py         # Kling video generation
│   ├── nodes_runway.py        # Runway ML
│   ├── nodes_luma.py          # Luma AI
│   ├── nodes_wan.py           # Wan video
│   └── [18 more provider files]
│
├── app/                       # Application-layer managers
│   ├── user_manager.py        # User settings, auth, session mapping
│   ├── model_manager.py       # Model file listing and management
│   ├── custom_node_manager.py # Custom node loading/disabling
│   ├── frontend_management.py # Frontend version management & static serving
│   ├── subgraph_manager.py    # Subgraph (blueprint) registration
│   ├── node_replace_manager.py# Node aliasing/replacement
│   ├── logger.py              # Log capture for /internal/logs
│   ├── app_settings.py        # Per-user/global settings persistence
│   └── database/              # SQLAlchemy models + Alembic migrations
│
├── api_server/
│   ├── routes/internal/       # /internal/* routes (logs, folder_paths, files)
│   └── services/              # TerminalService, etc.
│
├── comfy_extras/              # Extra built-in nodes (upscalers, video, 3D, audio, etc.)
├── middleware/                # aiohttp middlewares (cache_control, etc.)
├── model_filemanager/         # File browsing for model explorer
│
├── web/                       # Frontend React SPA (bundled JS/CSS)
│   └── extensions/core/       # Core JS extensions (always tracked, not gitignored)
│
├── user/                      # Per-user data (gitignored)
│   └── HLWUser.bat            # HLW startup script — sets COMFY_API_KEY, launches app
│
├── models/                    # Model weights storage (gitignored)
├── input/ / output/ / temp/   # I/O directories (gitignored)
├── custom_nodes/              # Third-party node packages (gitignored, except examples)
│
├── blueprints/                # Pre-built workflow JSON templates
├── .agent/
│   ├── rules/                 # Agent behaviour rules
│   └── workflows/             # Agent workflow guides (update-comfyui.md, etc.)
│
├── requirements.txt           # Core pip dependencies
├── pyproject.toml             # Project metadata, version, lint config
└── README.md                  # HLW-specific operational documentation
```

---

## 4. Runtime Startup Flow

```
user/HLWUser.bat
  └─ sets COMFY_API_KEY env var
  └─ python main.py [--listen ...] [--port 8188]

main.py
  1. comfy.options.enable_args_parsing()   # parse CLI args
  2. setup_logger()
  3. comfy_aimdo.control.init()            # dynamic VRAM controller (RTX 5090 optimized)
  4. apply_custom_paths()                  # register model directories from extra_model_paths.yaml
  5. execute_prestartup_script()           # run prestartup_script.py in each custom_node/
  6. init_custom_nodes()                   # import all custom_nodes, build NODE_CLASS_MAPPINGS
  7. import server.PromptServer            # create aiohttp app
  8. PromptServer.start()                  # bind port, run event loop
```

---

## 5. Core Execution Pipeline

When the frontend submits a workflow ("prompt"), this is the execution path:

```
Frontend (WebSocket) → PromptServer.queue_prompt()
  └─ execution.PromptQueue.put()
  └─ execution.PromptExecutor.execute()
       ├─ DynamicPrompt(original_prompt)        # wrap the JSON prompt graph
       ├─ ExecutionList.stage_node_execution()   # topological sort / dependency resolve
       ├─ CacheKeySet.add_keys()                # compute cache keys (by ID or input hash)
       └─ loop: execute each node in order
            ├─ validate_node_input()            # type-check all inputs
            ├─ get_output_data()
            │    ├─ [v3 node] PREPARE_CLASS_CLONE → build_nested_inputs → execute(cls, ...)
            │    └─ [v1 node] getattr(obj, FUNCTION)(**inputs)
            ├─ HLW injection (v1 only):
            │    if v3_data is None and API_NODE: inject comfy_api_key
            └─ cache result → send progress/preview over WebSocket
```

### Node Version Types

| | V1 Node | V3 Node (v0.16+) |
|---|---|---|
| Base class | `ComfyNodeABC` | `IO.ComfyNode` |
| Schema | `INPUT_TYPES()` + `RETURN_TYPES` | `define_schema()` → `IO.Schema(...)` |
| Execution fn | `FUNCTION = "api_call"` → `api_call(self, ...)` | `async def execute(cls, ...)` |
| Auth wiring | `"hidden": {"comfy_api_key": "API_KEY_COMFY_ORG"}` | `IO.Hidden.api_key_comfy_org` in schema |
| Dispatch | Direct method call | `EXECUTE_NORMALIZED_ASYNC` wrapper chain |

---

## 6. Model Loading Pipeline

```
nodes.CheckpointLoaderSimple.load_checkpoint(ckpt_name)
  └─ folder_paths.get_full_path("checkpoints", ckpt_name)
  └─ comfy.sd.load_checkpoint_guess_config()
       ├─ comfy.model_detection.detect_model_class()  # identify arch (SD1, SDXL, Flux, WAN...)
       ├─ comfy.sd.load_model_weights() → ModelPatcher(model, load_device, offload_device)
       ├─ load CLIP text encoder(s)
       └─ load VAE
```

Models live in `models/` subdirectories and are indexed at startup by `folder_paths.py`.

**VRAM management** is automatic: `model_management.py` tracks a `VRAMState` enum (`NO_VRAM` → `HIGH_VRAM`) and routes models to CPU/GPU with on-demand loading via `ModelPatcher.patch_model()`.

---

## 7. API Node System (Cloud Inference)

All cloud API nodes live in `comfy_api_nodes/`. A v3 node follows this pattern:

```python
class GeminiImage(IO.ComfyNode):
    @classmethod
    def define_schema(cls):
        return IO.Schema(
            node_id="GeminiImageNode",
            inputs=[...],
            outputs=[IO.Image.Output()],
            hidden=[IO.Hidden.auth_token_comfy_org, IO.Hidden.api_key_comfy_org, IO.Hidden.unique_id],
            is_api_node=True,
        )

    @classmethod
    async def execute(cls, prompt, model, seed, images=None, ...) -> IO.NodeOutput:
        response = await sync_op(cls, ApiEndpoint(path="..."), data=..., response_model=...)
        return IO.NodeOutput(image, text)
```

### Authentication Chain (v3 nodes)

```
execute() calls sync_op(cls, endpoint, data, ...)
  └─ _helpers.get_auth_header(node_cls)
       1. node_cls.hidden.auth_token_comfy_org  → "Authorization: Bearer <token>"
       2. os.environ["COMFY_API_KEY"]           → "X-API-KEY: <key>"  ← HLW default path
       3. node_cls.hidden.api_key_comfy_org     → "X-API-KEY: <key>"  (UI fallback)
```

### Authentication Chain (v1 nodes)

```
execution.py:_async_map_node_over_list()
  if v3_data is None and API_NODE:
      inputs["comfy_api_key"] = os.getenv("COMFY_API_KEY")   ← HLW injection

api_call(self, ..., comfy_api_key, auth_token, ...)
  └─ SynchronousOperation(endpoint, request, auth_kwargs).execute()
```

> **Critical rule:** The `v3_data is None` guard in `execution.py` (line ~284) MUST be maintained after every upstream merge. Without it, v3 nodes crash with `unexpected keyword argument 'comfy_api_key'`.

---

## 8. Key Configuration Points

| Config | Location | Purpose |
|---|---|---|
| `COMFY_API_KEY` | `user/HLWUser.bat` | API key for all cloud nodes (auto-injected) |
| Model paths | `extra_model_paths.yaml` | Mount external model directories (gitignored) |
| CLI args | `comfy/cli_args.py` | All runtime flags (`--listen`, `--port`, `--cuda-device`, etc.) |
| Frontend version | `app/frontend_management.py` | React app version pinning |
| Node mappings | `nodes.py` + custom_nodes `__init__.py` | `NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS` |
| Quantized models | `comfy_kitchen` (pip package) | FP8/NVFP4 support for Flux, Qwen |

---

## 9. HLW-Specific Modifications

These files differ from upstream and must be preserved during merges:

| File | Change | Why |
|---|---|---|
| `execution.py` | `v3_data is None` guard on API key injection (line ~284) | v3 nodes crash without it |
| `execution.py` | `patch_api_client_operations()` to wrap `SynchronousOperation.execute` as async | Krita integration compatibility |
| `comfy_api_nodes/util/_helpers.py` | `get_auth_header()` reads `COMFY_API_KEY` env var | Auto-auth for all v3 API nodes |
| `comfy_api_nodes/mapper_utils.py` | `model_field_to_node_input()` utility | Not in upstream; used in local nodes |
| `comfy_api_nodes/apis/request_logger.py` | Request logging for debugging | Not in upstream |
| `execution_upstream.py` | Clean upstream `execution.py` copy | Reference for future merges |
| `user/HLWUser.bat` | Sets env vars and launches ComfyUI | HLW startup script |

---

## 10. Upstream Merge Procedure (Summary)

Full steps in [.agent/workflows/update-comfyui.md](.agent/workflows/update-comfyui.md). Key steps:

```bash
git stash push -u -m "wip-before-vX.Y.Z-update"
git checkout -b update/vX.Y.Z
git fetch upstream
git merge vX.Y.Z              # resolve conflicts: keep HLW changes in execution.py
git stash pop
# fix any post-merge import errors (see README.md § Post-Update Import Fix)
git add -A && git commit
git checkout master && git merge update/vX.Y.Z
git branch -d update/vX.Y.Z
git push origin master
```

**Most common conflict:** `execution.py` — always preserve the `v3_data is None` guard and `patch_api_client_operations()` block. Take upstream for all other files unless there's a specific HLW reason.

---

## 11. WebSocket API (Frontend ↔ Server)

`server.py` is the communication hub. Key WebSocket message types (defined in `protocol.py`):

| Event | Direction | Meaning |
|---|---|---|
| `executing` | Server → Client | Node currently running |
| `execution_cached` | Server → Client | Node skipped (cache hit) |
| `progress` | Server → Client | Progress bar update |
| `preview_image` | Server → Client | Inline latent preview |
| `executed` | Server → Client | Node finished, outputs available |
| `execution_error` | Server → Client | Node threw an exception |
| `queue_prompt` | Client → Server | Submit a new workflow |
| `interrupt` | Client → Server | Cancel current execution |

REST endpoints are registered in `server.py` and `api_server/routes/`.

---

## 12. Custom Node Loading

```
main.py:init_custom_nodes()
  for each folder in folder_paths["custom_nodes"]:
      import <module>
      NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
      NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)
```

A custom node package is any folder under `custom_nodes/` with a Python `__init__.py` (or `.py` file) that exports `NODE_CLASS_MAPPINGS`. The `custom_nodes/` directory is gitignored except `example_node.py.example`.
