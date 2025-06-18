import psutil
import os

def get_memory_usage_mb() -> float:
    process = psutil.Process(os.getpid())
    mem_bytes = process.memory_info().rss  # Resident Set Size
    return mem_bytes / 1024 / 1024  # MB 단위
