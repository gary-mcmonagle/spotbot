import os
from waitress import serve
from src.app import application

serve(application,host="0.0.0.0",port=os.environ["PORT"])