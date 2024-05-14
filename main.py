from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from database import Base, engine, SessionLocal, Task

app = FastAPI()

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str
    completed: bool

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/createTask", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(title=task.title)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.get("/getTaskByID/{task_id}", response_model=TaskResponse)
def get_task_by_id(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@app.get("/getTaskByTitle/{title}", response_model=List[TaskResponse])
def get_task_by_title(title: str, db: Session = Depends(get_db)):
    db_tasks = db.query(Task).filter(Task.title == title).all()
    if not db_tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found with title '{title}'")
    return db_tasks

@app.delete("/deleteByID/{task_id}")
def delete_task_by_id(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted successfully"}

@app.delete("/deleteByTitle/{title}")
def delete_task_by_title(title: str, db: Session = Depends(get_db)):
    db_tasks = db.query(Task).filter(Task.title == title).all()
    if not db_tasks:
        raise HTTPException(status_code=404, detail=f"No tasks found with title '{title}'")
    for db_task in db_tasks:
        db.delete(db_task)
    db.commit()
    return {"message": f"All tasks with title '{title}' deleted successfully"}

@app.delete("/deleteAll")
def delete_all_tasks(db: Session = Depends(get_db)):
    db.query(Task).delete()
    db.commit()
    return {"message": "All tasks deleted successfully"}

@app.get("/getAllTasks", response_model=List[TaskResponse])
def get_all_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@app.put("/updateTask/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, updated_task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.title = updated_task.title
    db_task.completed = updated_task.completed
    db.commit()
    db.refresh(db_task)
    return db_task

