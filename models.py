from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    id: str
    user_id: str
    user_name: str
    timestamp: str
    message: str
