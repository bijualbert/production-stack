import os
import sys
from types import SimpleNamespace

from fastapi import FastAPI

# Add src/ so vllm_router can be imported
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)
# fmt: off
from vllm_router.app import app as router_app  # type: ignore
from vllm_router.app import initialize_all  # type: ignore
# fmt: on

# Vercel needs a literal `app = FastAPI()` in this file
app = FastAPI()


def _init_router_from_env():
    """
    Initialize production-stack router singletons in 'static' mode for serverless.
    Required env vars:
      ROUTER_STATIC_BACKENDS: comma-separated URLs (e.g. https://my-vllm-1.example.com,http://1.2.3.4:8000)
      ROUTER_STATIC_MODELS: comma-separated model ids aligned with backends
    Optional:
      ROUTER_ROUTING_LOGIC: roundrobin|session (default: roundrobin)
      ROUTER_SESSION_KEY: header key for session routing
    """
    static_backends = os.getenv("ROUTER_STATIC_BACKENDS", "").strip()
    static_models = os.getenv("ROUTER_STATIC_MODELS", "").strip()

    if not static_backends or not static_models:
        # Don't crash the function; expose health endpoint that explains missing config.
        # You can also raise here if you prefer hard-fail.
        return False

    args = SimpleNamespace(
        # required
        service_discovery="static",
        routing_logic=os.getenv("ROUTER_ROUTING_LOGIC", "roundrobin"),
        session_key=os.getenv("ROUTER_SESSION_KEY"),
        # static discovery params
        static_backends=static_backends,
        static_models=static_models,
        static_aliases=None,
        static_model_types=None,
        static_model_labels=None,
        static_backend_health_checks=False,
        prefill_model_labels=None,
        decode_model_labels=None,
        # k8s params (unused)
        k8s_service_discovery_type=None,
        k8s_namespace="default",
        k8s_port="8000",
        k8s_label_selector=None,
        k8s_watcher_timeout_seconds=0,
        backend_health_check_timeout_seconds=10,
        # monitoring
        engine_stats_interval=30,
        request_stats_window=60,
        # optional subsystems
        enable_batch_api=False,
        batch_processor=None,
        file_storage_class=None,
        file_storage_path=None,
        # dynamic config (unused here)
        dynamic_config_yaml=None,
        dynamic_config_json=None,
        # callbacks, feature gates
        callbacks=None,
        feature_gates="",
        # semantic cache options (off)
        semantic_cache_model=None,
        semantic_cache_dir=None,
        semantic_cache_threshold=0.0,
        # tracing/sentry (off)
        sentry_dsn=None,
        sentry_traces_sample_rate=0.0,
        sentry_profile_session_sample_rate=0.0,
        otel_endpoint=None,
        otel_service_name=None,
        otel_secure=False,
        # misc flags
        log_stats=False,
        log_stats_interval=30,
        host="0.0.0.0",
        port=8000,
        kv_aware_threshold=2000,
        lmcache_controller_port=0,
        lmcache_health_check_interval=5,
        lmcache_worker_timeout=30,
    )

    initialize_all(router_app, args)
    return True


_initialized = _init_router_from_env()


@app.get("/healthz")
def healthz():
    if not _initialized:
        return {
            "status": "not-initialized",
            "hint": "Set ROUTER_STATIC_BACKENDS and ROUTER_STATIC_MODELS env vars in Vercel.",
        }
    return {"status": "ok"}


# Mount the real router at /
app.mount("/", router_app)
