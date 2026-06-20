"""
Entry point for the daily pipeline. This is what cron runs.

    python run_pipeline.py
"""

from app.pipeline import run

if __name__ == "__main__":
    run()
