"""
LLM Weather Summarizer
A Python application that uses Large Language Models to provide intelligent weather summaries.

Date: July 2025
"""

import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from data import *
from decoderService import GeocodingService

class ApiRequest:
    """Generic API request handler"""
    
    def __init__(self, url: str, headers: Optional[Dict[str, str]] = None):
        self.url = url
        self.headers = headers or {"Content-Type": "application/json"}
        
    def send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send POST request and return response"""
        try:
            response = requests.post(self.url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {e}")


class WeatherApiRequest:
    """Specialized weather API request handler"""
    
    def __init__(self, config: WeatherConfig):
        self.config = config
        
    def get_weather_data(self, latitude: float, longitude: float, 
                        current: List[str] = None, daily: List[str] = None) -> Dict[str, Any]:
        """Get weather data for specified location"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": current or ["temperature_2m", "relative_humidity_2m", "weather_code"],
            "daily": daily or ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.config.url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Weather API request failed: {e}")


class LLMHandler:
    """Handler for LLM interactions"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.api_request = ApiRequest(config.ollama_api, config.headers)
        
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from LLM."""
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = self.api_request.send_request(payload)
            return response.get('message', {}).get('content', '')
        except Exception as e:
            return f"Error generating response: {e}"


class WeatherSummarizer:
    """Main weather summarizer class"""
    
    def __init__(self, model_config: ModelConfig = None, weather_config: WeatherConfig = None):
        self.model_config = model_config or ModelConfig()
        self.weather_config = weather_config or WeatherConfig()
        self.llm_handler = LLMHandler(self.model_config)
        self.weather_api = WeatherApiRequest(self.weather_config)
        
    def greet_user(self) -> str:
        """Generate greeting message for user"""
        messages = [
            {
                "role": "system",
                "content": "You are a helpful weather assistant. Provide a brief, friendly greeting and ask the user for their location and what weather information they need. Keep it concise - no more than 3 sentences."
            },
            {
                "role": "user", 
                "content": "Greet the user and ask for their weather needs."
            }
        ]
        
        return self.llm_handler.generate_response(messages)
    
    def parse_user_request(self, user_input: str) -> Dict[str, Any]:
        """Parse user request to extract location and weather requirements"""
        
        # Check if the input looks like coordinates
        geocoder = GeocodingService()
        coords = geocoder._is_coordinate_pair(user_input)
        if coords:
            return {
                "location": f"{coords[0]}, {coords[1]}",
                "latitude": coords[0],
                "longitude": coords[1],
                "weather_type": "current",
                "specific_requirements": "weather information for coordinates"
            }
        
        # Use LLM to parse natural language input
        messages = [
            {
                "role": "system",
                "content": """Extract location and weather info from user input. Respond ONLY with valid JSON:

                {
                    "location": "city name or coordinates",
                    "latitude": null,
                    "longitude": null,
                    "weather_type": "current or forecast", 
                    "specific_requirements": "what they want"
                }
                
                Do NOT include markdown formatting, backticks, or explanations. Only pure JSON."""
            },
            {
                "role": "user",
                "content": f"Parse this: {user_input}"
            }
        ]
        
        response = self.llm_handler.generate_response(messages=messages)
        
        # Clean the response to extract JSON
        cleaned_response = self._extract_json(response)
        
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError:
            return {
                "location": "unknown",
                "latitude": None,
                "longitude": None,
                "weather_type": "current",
                "specific_requirements": user_input,
                "raw_response": response
            }
    
    def _extract_json(self, response: str) -> str:
        """Extract JSON from LLM response that may contain markdown"""
        cleaned = response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in cleaned:
            start = cleaned.find("```json") + 7
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        
        # Find JSON object in the response
        json_start = cleaned.find('{')
        json_end = cleaned.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            cleaned = cleaned[json_start:json_end]
        
        return cleaned
            
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get coordinates for a location using geocoding service"""
        if not hasattr(self, 'geocoding_service'):
            self.geocoding_service = GeocodingService()
        
        return self.geocoding_service.get_coordinates(location)
    
    def summarize_weather_data(self, weather_data: Dict[str, Any], user_requirements: str) -> str:
        """Summarize weather data based on user requirements"""
        messages = [
            {
                "role": "system",
                "content": """You are a weather data summarizer. Provide a clear, concise weather summary.

                Format requirements:
                - Use simple headers (# ## ###)
                - Keep it brief and conversational
                - Include current temperature, conditions, and forecast
                - Don't repeat information
                - No excessive formatting or decorative elements
                - Maximum 150 words
                
                Example format:
                # Weather in [City]
                
                ## Current Conditions
                Temperature: X°C, Condition details
                
                ## Today's Forecast
                High/Low temperatures and key details"""
            },
            {
                "role": "user",
                "content": f"User requested: {user_requirements}\n\nWeather data: {json.dumps(weather_data, indent=2)}"
            }
        ]
        
        return self.llm_handler.generate_response(messages)

    def display_summary(self, summary: str):
        """Display the weather summary with clean formatting"""
        formatted_text = self._clean_markdown(summary)
        print(formatted_text)
    
    def _clean_markdown(self, text: str) -> str:
        """Clean markdown and format for console display"""
        cleaned = text
        
        # Replace headers with emojis
        cleaned = cleaned.replace('### ', '🌡️ ')
        cleaned = cleaned.replace('## ', '📍 ')
        cleaned = cleaned.replace('# ', '🌤️ ')
        
        # Clean up markdown formatting
        cleaned = cleaned.replace('**', '')
        cleaned = cleaned.replace('__', '')
        cleaned = cleaned.replace('- ', '  • ')
        cleaned = cleaned.replace('* ', '  • ')
        
        # Clean up multiple newlines
        while '\n\n\n' in cleaned:
            cleaned = cleaned.replace('\n\n\n', '\n\n')
        
        return cleaned.strip()

    def run(self):
        """Main execution flow"""
        print("=== Weather Summarizer ===\n")
        
        # Greet user
        greeting = self.greet_user()
        self.display_summary(greeting)
        
        # Get user input
        user_input = input("\nYour input: ")
        
        # Parse user request
        parsed_request = self.parse_user_request(user_input)
        
        # Get coordinates if not provided
        if not parsed_request.get('latitude') or not parsed_request.get('longitude'):
            location = parsed_request.get('location', 'London')
            lat, lon = self.get_coordinates(location)
            parsed_request['latitude'] = lat
            parsed_request['longitude'] = lon
        
        try:
            # Get weather data
            weather_data = self.weather_api.get_weather_data(
                parsed_request['latitude'],
                parsed_request['longitude']
            )
            
            # Summarize weather data
            summary = self.summarize_weather_data(
                weather_data, 
                parsed_request.get('specific_requirements', user_input)
            )
            
            # Display summary
            print("\n=== Weather Summary ===")
            self.display_summary(summary)
            
        except Exception as e:
            error_message = f"**Error**: Unable to fetch weather data. {str(e)}"
            self.display_summary(error_message)

def main():
    """Main function to run the weather summarizer."""
    model_config = ModelConfig()
    weather_config = WeatherConfig()
    
    summarizer = WeatherSummarizer(model_config, weather_config)
    summarizer.run()

if __name__ == "__main__":
    main()