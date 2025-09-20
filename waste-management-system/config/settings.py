import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    This centralized configuration makes it easy to manage different environments
    """
    
    # API Keys
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./waste_management.db")
    
    # Redis Cache
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Application Settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    # API Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    
    # LLM Configuration
    llm_model: str = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create global settings instance
settings = Settings()

# Validation function to check if required settings are present
def validate_settings():
    """Validate that all required settings are configured"""
    required_settings = {
        "OPENAI_API_KEY": settings.openai_api_key,
    }
    
    missing_settings = [
        setting for setting, value in required_settings.items() 
        if not value or value == ""
    ]
    
    if missing_settings:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_settings)}\n"
            f"Please check your .env file and ensure these are set."
        )
    
    print("✅ Configuration validated successfully!")
    return True

if __name__ == "__main__":
    # Test the configuration
    validate_settings()
    print(f"Environment: {settings.environment}")
    print(f"LLM Model: {settings.llm_model}")
    print(f"Database: {settings.database_url}")