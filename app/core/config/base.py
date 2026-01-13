from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Calculate path to project root (3 levels up from config/base.py)
ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / f".env"

# Try to load environment file if it exists, otherwise use system environment variables
# if ENV_FILE.exists():
#
# else:
#     import warnings
#     warnings.warn(
#         f"Environment file {ENV_FILE} does not exist. "
#         "Using system environment variables.",
#         UserWarning
#     )

load_dotenv(override=True)

class EnvBaseSettings(BaseSettings):
    """Base settings class that loads environment variables.
    
    All settings should inherit from this class.
    """

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields not defined in the model

