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

## Recent Changes

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

