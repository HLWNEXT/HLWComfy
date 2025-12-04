import torch
# Disable FP8 operations
torch.backends.cuda.matmul.allow_fp8 = False
if hasattr(torch, '_scaled_mm'):
    torch._scaled_mm = None
print("FP8 operations disabled")