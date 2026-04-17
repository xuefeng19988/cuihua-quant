"""
Phase 69: Async Processing Engine
Asynchronous task processing for better performance.
"""

import os
import sys
import asyncio
import time
import functools
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
from queue import Queue
import threading

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class TaskResult:
    """Task execution result."""
    def __init__(self, task_id: str, status: str, result: Any = None, 
                 error: str = None, duration: float = 0):
        self.task_id = task_id
        self.status = status
        self.result = result
        self.error = error
        self.duration = duration
        self.completed_at = datetime.now()


class AsyncTaskEngine:
    """
    Async task processing engine with thread pool.
    """
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = Queue()
        self.results: Dict[str, TaskResult] = {}
        self._running = False
        self._lock = threading.Lock()
        
    def submit(self, func: Callable, *args, **kwargs) -> str:
        """
        Submit a task for async execution.
        
        Returns:
            Task ID
        """
        import uuid
        task_id = str(uuid.uuid4())[:8]
        
        def wrapper():
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                with self._lock:
                    self.results[task_id] = TaskResult(
                        task_id, 'completed', result, duration=duration
                    )
                return result
            except Exception as e:
                duration = time.time() - start
                with self._lock:
                    self.results[task_id] = TaskResult(
                        task_id, 'failed', error=str(e), duration=duration
                    )
                return None
                
        self.executor.submit(wrapper)
        return task_id
        
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """Get task result by ID."""
        with self._lock:
            return self.results.get(task_id)
            
    def is_completed(self, task_id: str) -> bool:
        """Check if task is completed."""
        result = self.get_result(task_id)
        return result is not None and result.status in ['completed', 'failed']
        
    def wait_for_result(self, task_id: str, timeout: float = 30) -> Optional[TaskResult]:
        """Wait for task result with timeout."""
        start = time.time()
        while time.time() - start < timeout:
            result = self.get_result(task_id)
            if result:
                return result
            time.sleep(0.1)
        return None
        
    def submit_batch(self, func: Callable, items: List, *args, **kwargs) -> List[str]:
        """
        Submit multiple tasks in batch.
        
        Returns:
            List of task IDs
        """
        return [self.submit(func, item, *args, **kwargs) for item in items]
        
    def wait_for_batch(self, task_ids: List[str], timeout: float = 60) -> Dict[str, TaskResult]:
        """Wait for all tasks in batch to complete."""
        results = {}
        start = time.time()
        
        while time.time() - start < timeout:
            all_done = True
            for task_id in task_ids:
                if task_id not in results:
                    result = self.get_result(task_id)
                    if result:
                        results[task_id] = result
                    else:
                        all_done = False
                        
            if all_done:
                break
            time.sleep(0.1)
            
        return results
        
    def get_stats(self) -> Dict:
        """Get engine statistics."""
        with self._lock:
            completed = sum(1 for r in self.results.values() if r.status == 'completed')
            failed = sum(1 for r in self.results.values() if r.status == 'failed')
            
        return {
            'max_workers': self.max_workers,
            'total_tasks': len(self.results),
            'completed': completed,
            'failed': failed,
            'pending': len(self.results) - completed - failed
        }
        
    def shutdown(self):
        """Shutdown the engine."""
        self.executor.shutdown(wait=True)
        self._running = False


class AsyncDataFetcher:
    """
    Async data fetching with connection pooling.
    """
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def fetch_with_limit(self, func: Callable, *args, **kwargs) -> Any:
        """Fetch data with concurrency limit."""
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))
            
    async def fetch_multiple(self, func: Callable, items: List, 
                            *args, **kwargs) -> Dict:
        """Fetch data for multiple items concurrently."""
        tasks = [self.fetch_with_limit(func, item, *args, **kwargs) for item in items]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            item: result if not isinstance(result, Exception) else str(result)
            for item, result in zip(items, results)
        }


def async_task(engine: AsyncTaskEngine):
    """
    Decorator to submit function as async task.
    
    Usage:
        @async_task(my_engine)
        def my_function(data):
            return process(data)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return engine.submit(func, *args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    print("✅ Async Processing Engine modules loaded")
    
    # Test engine
    engine = AsyncTaskEngine(max_workers=4)
    
    def slow_task(n):
        time.sleep(0.5)
        return n * 2
        
    # Submit tasks
    task_ids = engine.submit_batch(slow_task, list(range(10)))
    print(f"\n📊 Submitted {len(task_ids)} tasks")
    
    # Wait for results
    results = engine.wait_for_batch(task_ids, timeout=10)
    print(f"✅ Completed: {len(results)} tasks")
    
    # Print stats
    stats = engine.get_stats()
    print(f"\n📈 Engine Stats:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
        
    engine.shutdown()
