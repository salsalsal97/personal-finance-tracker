import os
from dotenv import load_dotenv

load_dotenv()

# Anthropic (for PDF -> CSV conversion only, if needed)
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
DATABASE_URI: str = os.environ["DATABASE_URI"]
SECRET_KEY: str = os.environ["SECRET_KEY"]