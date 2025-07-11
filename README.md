🌤️ LLM Weather Summarizer

A Python application that uses Large Language Models (LLMs) to provide intelligent, conversational weather summaries. The application integrates Ollama for natural language processing with Open-Meteo API for accurate weather data.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

✨ Features

1) LLM-Powered: Uses local LLM via Ollama for natural language understanding
2) Smart Geocoding: Automatically converts city names to coordinates using free APIs
3) Coordinate Support: Accepts both city names and latitude/longitude coordinates
4) Real Weather Data: Integrates with Open-Meteo API for accurate weather information
5) Intelligent Summarization: Provides contextual weather summaries based on user needs
6) Easy Setup: No API keys required for basic functionality

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🎯 Example Usage
=== Weather Summarizer ===
Hello! I'd love to help you with your weather needs today. 
Can you please tell me where you are located?

Your input: What's the weather like in Tokyo tomorrow?

🌤️ Weather in Tokyo Tomorrow
📍 Current Conditions
Temperature: 25°C, Humidity 70%, Clear skies
📍 Tomorrow's Forecast  
High: 28°C, Low: 21°C, Partly cloudy with light rain possible

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🛠️ Installation
Prerequisites:
1) Python 3.8 or higher
2) Ollama installed and running locally
3) Internet connection for weather data

Step 1: Clone the Repository. 
git clone https://github.com/yourusername/llm-weather-summarizer.git
cd llm-weather-summarizer

Step 2: Install Dependencies

Step 3: Install and Configure Ollama
Install Ollama from https://ollama.ai

Pull the required model:
ollama pull llama3.2

Start Ollama (it should run on http://localhost:11434 by default)

Step 4: Run the Application
python main.py

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🔧 Configuration
The application uses two main configuration classes:

1) ModelConfig (LLM Settings)
pythonModelConfig(
    ollama_api="http://localhost:11434/api/chat",  # Ollama API endpoint
    model="llama3.2",                              # LLM model name
    headers={"Content-Type": "application/json"}   # HTTP headers
)

2) WeatherConfig (Weather API Settings)
pythonWeatherConfig(
    url="https://api.open-meteo.com/v1/forecast"   # Weather API endpoint
)

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

🌍 Supported Input Formats
The application intelligently handles various input formats:

City Names:

"Tokyo"

"New York"

"London, UK"

Coordinates:

"40.7128, -74.0060"

"( 66.160507, -153.369141 )"

"51.5074 -0.1278"

Natural Language Requests:

"What's the weather like in Paris tomorrow?"

"Give me the forecast for coordinates 35.6762, 139.6503"

"Current conditions in Sydney"
