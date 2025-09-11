---
description: How to correctly install a custom ComfyUI node and its dependencies.
---
# Workflow: Install ComfyUI Custom Node

Use this workflow to properly clone and map a new custom node within the `HLWComfy` workspace.

// turbo-all
1. Navigate to the custom nodes directory:
   `cd custom_nodes`
2. Clone the requested node repository:
   `git clone <repository_url>`
3. Navigate into the newly cloned directory.
4. Check if a `requirements.txt` exists. If so, install its Python packages using pip, or use conda if specific native libraries are required:
   `pip install -r requirements.txt`
5. Print a success message confirming the custom node installation and remind the user to restart the ComfyUI server.
