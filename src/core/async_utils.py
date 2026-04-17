"""
Phase 17.3: Async processing utilities.
"""

import os
import sys
import asyncio
import concurrent.futures
from typing import List, Callable, Any, Dict, Coroutine
from datetime import datetime

class AsyncProcessor:
    """
    Async processing utilities for data fetching and signal generation.
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self._loop: asyncio.AbstractEventLoop | None = None
        
    async def fetch_parallel(self, fetch_func: Callable, items: List[Any], **kwargs) -> Dict[str, Any]:
        """
        Fetch data for multiple items in parallel.
        
        Args:
            fetch_func: Async function to call for each item
            items: List of items to process
            **kwargs: Additional arguments
            
        Returns:
            Dict mapping item to result
        """
        semaphore = asyncio.Semaphore(self.max_workers)
        
        async def limited_fetch(item):
            async with semaphore:
                try:
                    if asyncio.iscoroutinefunction(fetch_func):
                        result = await fetch_func(item, **kwargs)
                    else:
                        loop = asyncio.get_event_loop()
                        result = await loop.run_in_executor(None, fetch_func, item)
                    return item, result
                except Exception as e:
                    return item, {"error": str(e)}
                    
        tasks = [limited_fetch(item) for item in items]
        results = await asyncio.gather(*tasks)
        
        return dict(results)
        
    def run_parallel(self, func: Callable, items: List[Any], **kwargs) -> Dict[str, Any]:
        """
        Run function in parallel using thread pool.
        
        Args:
            func: Function to call
            items: List of items
            **kwargs: Additional arguments
            
        Returns:
            Dict mapping item to result
        """
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_item = {
                executor.submit(func, item, **kwargs): item
                for item in items
            }
            for future in concurrent.futures.as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    results[item] = future.result()
                except Exception as e:
                    results[item] = {"error": str(e)}
                    
        return results
        
    async def run_async(self, coro: Coroutine) -> Any:
        """Run a single coroutine."""
        return await coro
        
    def run_batch(self, funcs: List[Callable], timeout: int = 300) -> List[Any]:
        """
        Run multiple functions with timeout.
        
        Returns:
            List of results
        """
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(func) for func in funcs]
            for future in concurrent.futures.as_completed(futures, timeout=timeout):
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append({"error": str(e)})
                    
        return results


class AsyncDataFetcher:
    """Async wrapper for data fetching operations."""
    
    def __init__(self, max_workers: int = 5):
        self.processor = AsyncProcessor(max_workers)
        
    async def fetch_stocks(self, fetch_func: Callable, codes: List[str]) -> Dict:
        """Fetch data for multiple stocks in parallel."""
        return await self.processor.fetch_parallel(fetch_func, codes)
        
    def fetch_stocks_sync(self, fetch_func: Callable, codes: List[str]) -> Dict:
        """Synchronous wrapper for parallel stock fetching."""
        return self.processor.run_parallel(fetch_func, codes)


class AsyncSignalGenerator:
    """Async signal generation for multiple strategies."""
    
    def __init__(self, max_workers: int = 5):
        self.processor = AsyncProcessor(max_workers)
        
    async def generate_parallel(self, strategies: Dict[str, Callable], data: Any) -> Dict:
        """Generate signals from multiple strategies in parallel."""
        async def run_strategy(name_func):
            name, func = name_func
            try:
                result = func(data)
                if asyncio.iscoroutine(result):
                    result = await result
                return name, result
            except Exception as e:
                return name, {"error": str(e)}
                
        tasks = [run_strategy(nf) for nf in strategies.items()]
        results = await asyncio.gather(*tasks)
        return dict(results)
