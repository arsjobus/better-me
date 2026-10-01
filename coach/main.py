import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import List

import httpx
import pyttsx3
import pytz
from dotenv import load_dotenv
from pydantic import BaseModel

from redis_client import RedisClient

TIMEZONE = pytz.timezone("Asia/Bangkok")

load_dotenv()

tts_engine = pyttsx3.init()


class Task(BaseModel):
    id: int
    title: str
    completed: bool
    last_updated: int
    next_timeout: int


redis_client = RedisClient(
    url=os.getenv("REDIS_URL"),
    token=os.getenv("REDIS_TOKEN"),
)


def fetch_all_tasks() -> List[Task]:
    task_keys = redis_client.get_all_task_keys()
    if not task_keys:
        return []

    task_data_list = redis_client.get_all_data_for_keys(task_keys)
    tasks: List[Task] = []
    for task_data in task_data_list:
        if task_data is None:
            continue
        task_data_json = json.loads(task_data)
        tasks.append(
            Task(
                id=task_data_json.get("id"),
                title=task_data_json.get("title") or "",
                completed=task_data_json.get("completed", False),
                last_updated=task_data_json.get(
                    "last_updated", int(datetime.now().timestamp() * 1000)
                ),
                next_timeout=task_data_json.get("next_timeout"),
            )
        )
    return tasks


def reset_due_tasks(tasks: List[Task]) -> List[Task]:
    current_time = datetime.now(TIMEZONE)
    current_time_ms = int(current_time.timestamp() * 1000)
    for task in tasks:
        if task.next_timeout > current_time_ms:
            continue

        next_wake_up = (current_time + timedelta(days=1)).replace(
            hour=8, minute=0, second=0, microsecond=0
        )
        task.last_updated = current_time_ms
        task.next_timeout = int(next_wake_up.timestamp() * 1000)
        task.completed = False
        redis_client.set_task(f"task:{task.id}", task.model_dump_json())
    return tasks


async def send_input_to_ollama(prompt: str) -> str:
    api_url = (os.getenv("OLLAMA_API_URL") or "http://localhost:11434/api").rstrip("/")
    payload = {
        "prompt": prompt,
        "model": os.getenv("OLLAMA_MODEL") or "qwen3:8b",
        "stream": False,
        "think": False,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(f"{api_url}/generate", json=payload)
        response.raise_for_status()
        return response.json().get("response", "").strip()


async def coach_incomplete_tasks(tasks: List[Task]) -> str:
    task_list = "\n".join(f"- {task.title}" for task in tasks)
    prompt = (
        "You are a concise, supportive accountability coach. Give a short spoken reminder "
        "about these incomplete tasks. Do not claim the user failed or completed anything "
        "beyond what the list says.\n\n"
        f"Incomplete tasks:\n{task_list}"
    )
    response = await send_input_to_ollama(prompt)
    if response:
        print(f"Coach: {response}", flush=True)
        tts_engine.say(response)
        tts_engine.runAndWait()
    return response


async def run_coach() -> None:
    poll_interval = max(1, int(os.getenv("COACH_POLL_INTERVAL_SECONDS", "60")))
    reminder_interval = max(1, int(os.getenv("COACH_REMINDER_INTERVAL_SECONDS", "1800")))
    last_reminder_signature = None
    last_reminder_time = 0.0

    print(
        f"Coach running; polling Redis every {poll_interval}s with "
        f"{reminder_interval}s reminder cooldown.",
        flush=True,
    )

    while True:
        try:
            tasks = reset_due_tasks(fetch_all_tasks())
            incomplete_tasks = [task for task in tasks if not task.completed][:3]
            if not incomplete_tasks:
                last_reminder_signature = None
                last_reminder_time = 0.0
            else:
                signature = tuple((task.id, task.title) for task in incomplete_tasks)
                now = time.monotonic()
                if (
                    signature != last_reminder_signature
                    or now - last_reminder_time >= reminder_interval
                ):
                    response = await coach_incomplete_tasks(incomplete_tasks)
                    if response:
                        last_reminder_signature = signature
                        last_reminder_time = time.monotonic()
        except Exception as error:
            print(f"Coach cycle failed: {error}", flush=True)

        await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    try:
        asyncio.run(run_coach())
    except KeyboardInterrupt:
        print("Coach stopped.", flush=True)