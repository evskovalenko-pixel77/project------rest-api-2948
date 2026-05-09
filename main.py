import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'auth'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'tasks_crud'))

from src.auth.main import app

