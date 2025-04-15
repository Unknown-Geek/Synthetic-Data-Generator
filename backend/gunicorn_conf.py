import os
import psutil

# Gunicorn config variables
workers_per_core_str = os.getenv("WORKERS_PER_CORE", "2")  # Optimized for HF Space (2 vCPUs)
web_concurrency_str = os.getenv("WEB_CONCURRENCY", None)
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "7860")  # Default HF Spaces port
bind_env = os.getenv("BIND", None)
use_loglevel = os.getenv("LOG_LEVEL", "info")

# Core logic: calculate workers
if web_concurrency_str:
    web_concurrency = int(web_concurrency_str)
    assert web_concurrency > 0
else:
    import multiprocessing
    workers_per_core = float(workers_per_core_str)
    default_web_concurrency = max(2, multiprocessing.cpu_count() * workers_per_core)
    web_concurrency = min(int(default_web_concurrency), 8)  # Cap at 8 workers for 16GB RAM

# Set worker threads based on available memory
total_memory = psutil.virtual_memory().total / (1024 * 1024 * 1024)  # GB
if total_memory < 8:
    worker_threads = 2
elif total_memory < 16:
    worker_threads = 4
else:
    worker_threads = 8

# Gunicorn config
if bind_env:
    bind = bind_env
else:
    bind = f"{host}:{port}"

workers = web_concurrency
threads = worker_threads
worker_class = "uvicorn.workers.UvicornWorker"
worker_tmp_dir = "/dev/shm" if os.path.isdir("/dev/shm") else None
keepalive = 120
timeout = 300  # Longer timeout for synthetic data generation
graceful_timeout = 30
accesslog = "-"  # Log to stdout
errorlog = "-"  # Log to stderr

# Log configuration
print(f"Gunicorn configuration:")
print(f"- Bind: {bind}")
print(f"- Workers: {workers}")
print(f"- Threads per worker: {threads}")
print(f"- Worker class: {worker_class}")
print(f"- Timeout: {timeout}s")