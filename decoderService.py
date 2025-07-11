import requests
import re
from typing import Optional, Tuple
from time import sleep

class GeocodingService:
    """Geocoding service based on API"""
    
    def __init__(self):
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'Weather-Summarizer/1.0'
        })
        
    def _is_coordinate_pair(self, location: str) -> Optional[Tuple[float, float]]:
        """Check if input is already coordinates (lat,lon or lat lon)"""
        
        # Clean the input - remove parentheses and extra spaces
        cleaned = location.strip().replace('(', '').replace(')', '').strip()
        
        coord_pattern = r'^(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)$'
        match = re.match(coord_pattern, cleaned)
        
        if match:
            try:
                lat, lon = float(match.group(1)), float(match.group(2))
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    return (lat, lon)
            except ValueError:
                pass
        return None
    
    def _geocode_nominatim(self, location: str) -> Optional[Tuple[float, float]]:
        """Geocode using free OpenStreetMap Nominatim API"""
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data:
                return (float(data[0]['lat']), float(data[0]['lon']))
                
        except Exception as e:
            print(f"Geocoding failed: {e}")
        return None
    
    def get_coordinates(self, location: str) -> Tuple[float, float]:
        """Get coordinates for a location using multiple free APIs
        
        Args:
            location: City name, address, or coordinates
            
        Returns:
            Tuple of (latitude, longitude)
        """
        # Check if input is already coordinates
        coords = self._is_coordinate_pair(location)
        if coords:
            return coords
        
        # Try geocoding with Nominatim
        coords = self._geocode_nominatim(location)
        if coords:
            return coords
        
        # Final fallback to major cities
        major_cities = {
            'london': (51.5074, -0.1278),
            'new york': (40.7128, -74.0060),
            'paris': (48.8566, 2.3522),
            'tokyo': (35.6762, 139.6503),
            'sydney': (-33.8688, 151.2093),
            'berlin': (52.5200, 13.4050),
            'madrid': (40.4168, -3.7038),
            'rome': (41.9028, 12.4964),
            'kyiv': (50.44973, 30.52474),
            'beijing': (39.9042, 116.4074)
        }
        
        location_lower = location.lower()
        for city, coords in major_cities.items():
            if city in location_lower:
                return coords
        
        # Default to London if nothing found
        print(f"Location '{location}' not found, defaulting to London")
        return (51.5074, -0.1278)