from dotenv import load_dotenv

from base import Driver

load_dotenv("env/.env")
load_dotenv("env/se-config.env")
Driver()