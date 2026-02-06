from sqlmodel import Session, select, col
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from app.models.task import Task, TaskCreate, TaskUpdate

class TaskService:
    @staticmethod
    def get_tasks(
        session: Session,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at"
    ) -> List[Task]:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            statement = statement.where(Task.is_completed == True)
        elif status == "pending":
            statement = statement.where(Task.is_completed == False)

        if priority:
            statement = statement.where(Task.priority == priority)

        if search:
            statement = statement.where(col(Task.title).ilike(f"%{search}%"))

        # Basic sorting
        if sort_by == "priority":
            statement = statement.order_by(Task.priority)
        elif sort_by == "title":
            statement = statement.order_by(Task.title)
        else:
            statement = statement.order_by(Task.created_at.desc())

        return session.execute(statement).all()

    @staticmethod
    def create_task(session: Session, task_data: TaskCreate, user_id: uuid.UUID) -> Task:
        db_task = Task.model_validate(task_data, update={"user_id": user_id})
        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    @staticmethod
    def update_task(
        session: Session,
        task_id: uuid.UUID,
        task_data: TaskUpdate,
        user_id: uuid.UUID
    ) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = session.execute(statement).first()
        if not db_task:
            return None

        task_dict = task_data.model_dump(exclude_unset=True)
        for key, value in task_dict.items():
            setattr(db_task, key, value)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    @staticmethod
    def get_task_by_id(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        return session.execute(statement).first()

    @staticmethod
    def update_task_completion(
        session: Session,
        task_id: uuid.UUID,
        completed: bool,
        user_id: uuid.UUID
    ) -> Optional[Task]:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = session.execute(statement).first()
        if not db_task:
            return None

        db_task.is_completed = completed
        db_task.updated_at = datetime.now(timezone.utc)

        session.add(db_task)
        session.commit()
        session.refresh(db_task)
        return db_task

    @staticmethod
    def delete_task(session: Session, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        db_task = session.execute(statement).first()
        if not db_task:
            return False

        session.delete(db_task)
        session.commit()
        return True
