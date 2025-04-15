import os
import sys
import logging
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # For development use Uvicorn directly
    if os.getenv("ENVIRONMENT") == "development":
        import uvicorn
        port = int(os.getenv("PORT", 7860))
        logger.info(f"Starting development server on port {port} with hot reload")
        uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
    else:
        # For production use Gunicorn with Uvicorn workers
        logger.info("Starting production server with Gunicorn and Uvicorn workers")
        cmd = [
            "gunicorn",
            "-c", "gunicorn_conf.py",
            "-k", "uvicorn.workers.UvicornWorker",
            "app:app"
        ]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Error starting Gunicorn: {e}")
            sys.exit(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            sys.exit(0)