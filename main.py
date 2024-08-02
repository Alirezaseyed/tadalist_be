from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    description: str
    completed: bool

class TaskCreate(BaseModel):
    description: str

tasks_db = {
    "user1": [
        {"id": 1, "description": "Read the data from database", "completed": False},
        {"id": 2, "description": "Check user access", "completed": True},
        {"id": 3, "description": "Return only this user's tasks", "completed": False},
    ]
}

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/getAllTasks/{user_id}", response_model=List[Task])
def get_all_tasks_of_user(user_id: str):
    if user_id in tasks_db:
        return tasks_db[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/v1/addTask/{user_id}", response_model=Task)
def add_task(user_id: str, task: TaskCreate):
    if user_id not in tasks_db:
        tasks_db[user_id] = []

    new_task_id = max(task["id"] for task in tasks_db[user_id], default=0) + 1
    new_task = {"id": new_task_id, "description": task.description, "completed": False}
    tasks_db[user_id].append(new_task)
    return new_task

@app.put("/api/v1/updateTask/{user_id}/{task_id}", response_model=Task)
def update_task(user_id: str, task_id: int, task: TaskCreate):
    if user_id not in tasks_db:
        raise HTTPException(status_code=404, detail="User not found")

    task_to_update = next((t for t in tasks_db[user_id] if t["id"] == task_id), None)
    if task_to_update is None:
        raise HTTPException(status_code=404, detail="Task not found")

    task_to_update["description"] = task.description
    return task_to_update

@app.delete("/api/v1/deleteTask/{user_id}/{task_id}", response_model=dict)
def delete_task(user_id: str, task_id: int):
    if user_id not in tasks_db:
        raise HTTPException(status_code=404, detail="User not found")

    global tasks_db
    tasks_db[user_id] = [t for t in tasks_db[user_id] if t["id"] != task_id]
    return {"detail": "Task deleted"}
