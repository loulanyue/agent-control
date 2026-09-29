import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import Agent, Task, GraphDefinition, Rule, HzTalentNotice
from app.core.security import generate_ulid, hash_token

def test_ulid_generation():
    task_id = generate_ulid("TASK")
    assert task_id.startswith("TASK_")
    assert len(task_id) > 20

def test_token_hash():
    h = hash_token("test_secret")
    assert len(h) == 64

print("Unit tests passed successfully!")
