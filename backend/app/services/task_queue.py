"""Task queue service with Celery fallback."""
import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TaskQueueService:
    """Abstract task queue service."""
    
    def __init__(self):
        """Initialize task queue."""
        self.tasks = {}
        self.queue = asyncio.Queue()
    
    async def enqueue(self, task_type: str, task_id: str, payload: Dict[str, Any]) -> str:
        """Enqueue a task."""
        try:
            await self.queue.put({
                "task_type": task_type,
                "task_id": task_id,
                "payload": payload,
            })
            self.tasks[task_id] = {"status": "pending", "payload": payload}
            logger.info(f"Enqueued task {task_id}: {task_type}")
            return task_id
        except Exception as e:
            logger.error(f"Failed to enqueue task: {e}")
            raise
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status."""
        return self.tasks.get(task_id, {"status": "not_found"})
    
    def update_task_status(self, task_id: str, status: str, result: Dict[str, Any] = None):
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id]["status"] = status
            if result:
                self.tasks[task_id]["result"] = result


task_queue_service = TaskQueueService()


async def init_task_queue():
    """Initialize task queue."""
    logger.info("Task queue initialized")
