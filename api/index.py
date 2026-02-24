import os
import sys

# Add the src directory to the python path so that vllm_router can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from vllm_router.app import app
except ImportError:
    # Fallback to local import if packaging fails in Vercel
    from src.vllm_router.app import app

# This is the FastAPI entrypoint for Vercel.
