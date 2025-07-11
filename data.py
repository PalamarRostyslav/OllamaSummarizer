from typing import Dict
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for the LLM model"""
    ollama_api: str = "http://localhost:11434/api/chat"
    headers: Dict[str, str] = None
    model: str = "llama3.2"
    
    def __post_init__(self):
        if self.headers is None:
            self.headers = {"Content-Type":"application/json"}

@dataclass
class WeatherConfig:
    """Configuration for weather API"""
    url: str = "https://api.open-meteo.com/v1/forecast"
    