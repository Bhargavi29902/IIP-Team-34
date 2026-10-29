from rapidfuzz import fuzz

from ..models import Task


def find_duplicates(title: str, client_id: int | None, exclude_id: int | None = None,
                    threshold: int = 85) -> list[Task]:
    q = Task.query.filter(Task.status != "done")
    if client_id:
        q = q.filter(Task.client_id == client_id)
    return [t for t in q.all()
            if t.id != exclude_id and fuzz.token_set_ratio(title.lower(), t.title.lower()) >= threshold]
