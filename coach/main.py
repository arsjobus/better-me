import asyncio
import httpx
import json
import os
import pyttsx3
import pytz
from datetime import datetime, timedelta, time
from urllib.parse import urljoin
from dotenv import load_dotenv
from typing import List
from redis_client import RedisClient
from pydantic import BaseModel

TIMEZONE = pytz.timezone('Asia/Bangkok')

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
    token=os.getenv("REDIS_TOKEN")
)

# Global variable to hold conversation history
conversation_history = ""

async def start_in_ctx():
    global conversation_history
    context = "You will play the role as an accountability coach, say OK only"
    response = await send_input_to_ollama(context)
    conversation_history += f"{context}\n{response}\n"

async def analyze_data(data):
    global conversation_history
    instruction = "Scold me for not completing these tasks:"
    # Combine instruction with conversation history
    prompt = f"{conversation_history}{instruction}\n\n{data}"
    output = await send_input_to_ollama(prompt)
    conversation_history += f"{instruction}\n\n{data}\n{output}\n"
    tts_engine.say(output)
    tts_engine.runAndWait()

def fetch_all_tasks() -> List[Task]:
    task_keys = redis_client.get_all_task_keys()
    if not task_keys:
        return []
    task_data_list = redis_client.get_all_data_for_keys(task_keys)
    tasks: List[Task] = []
    for task_data in task_data_list:
        task_data_json = json.loads(task_data)
        tasks.append(
            Task(
                id = task_data_json.get('id'),
                title = task_data_json.get('title') or "",
                completed = task_data_json.get('completed') or False,
                last_updated = task_data_json.get('last_updated') or int(datetime.now().timestamp()),
                next_timeout = task_data_json.get('next_timeout') 
            )
        )
    return tasks

def reset_all_tasks(tasks: List[Task]):
    current_time = datetime.now(TIMEZONE)
    wake_up_time = current_time.replace(hour=8, minute=0, second=0, microsecond=0)
    for task in tasks:
        next_timeout = datetime.fromtimestamp(task.next_timeout / 1000, TIMEZONE)
        if wake_up_time >= next_timeout:
            tomorrow_at_8am = datetime.combine(current_time + timedelta(days=1), time(8, 0))
            task.last_updated = int(current_time.replace(tzinfo=None).timestamp())
            task.next_timeout = int(tomorrow_at_8am.replace(tzinfo=None).timestamp())
            task.completed = False
            redis_client.set_task(f"task:{task.id}", json.dumps(task.model_dump()))
    return tasks

async def send_input_to_ollama(prompt: str) -> str:
    url = urljoin(os.getenv("OLLAMA_API_URL"), "generate")
    payload = {
        "prompt": prompt,
        "model": os.getenv("OLLAMA_MODEL") or "llama3.2"
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        if response.status_code == 200:
            output = ""
            lines = response.text.split("\n")
            for line in lines:
                json_obj = json.loads(line or '{}')
                output += json_obj.get('response', "")
            return output
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return ""

if __name__ == "__main__":
    asyncio.run(start_in_ctx())
    tasks = fetch_all_tasks()
    task_list_for_ai = ""
    incomplete_tasks = ""
    counter = 0
    for i in range(0, len(tasks) - 1):
        if counter >= 3:
            break
        completion_status = "done" if tasks[i].completed else "not done"
        task_list_for_ai += f"{i+1}) {tasks[i].title} is {completion_status}\n"
        if not tasks[i].completed:
            counter += 1
            incomplete_tasks += f"{tasks[i].title} was not completed!\n"
    if len(incomplete_tasks) > 0:
        asyncio.run(analyze_data(incomplete_tasks))
    reset_all_tasks(tasks)