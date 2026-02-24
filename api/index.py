import os
import sys

# Add the src directory to the python path so that vllm_router can be imported
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

try:
    from vllm_router.app import app as router_app  # type: ignore
except ImportError:
    # Fallback to local import if packaging fails in Vercel
    from src.vllm_router.app import app as router_app  # type: ignore

# This is the FastAPI entrypoint for Vercel.
# Vercel's static analyzer requires finding a literal `app = FastAPI()` 
# assignment in this file to recognize it as a serverless function.
from fastapi import FastAPI

app = FastAPI()
app.mount("/", router_app)
