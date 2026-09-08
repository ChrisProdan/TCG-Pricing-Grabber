from __future__ import annotations

from dataclasses import dataclass

import os
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class Settings:
    
    db_host:str
    db_port:int
    db_name:str
    db_user:str
    db_password:str
    
def load_settings() -> Settings:
    
    return Settings(
        db_host=os.environ(["DB_HOST"]),
        db_port=int(os.environ(["DB_PORT"])),
        db_name=os.environ(["DB_NAME"]),
        db_user=os.environ(["DB_USER"]),
        db_password=os.environ(["DB_PASSWORD"])
    )
    
    
    



