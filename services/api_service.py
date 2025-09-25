import requests
import google.generativeai as genai
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

class APIService:
    def __init__(self):
        # Initialize APIs
        self.weather_api_key = "8ec8aac1ced747ec89655941252409"
        self.gemini_api_key = "AIzaSyBIA0VRcgOtGImuIa2HSIaAcLAyxM6UYM4"
        self.market_api_key = "579b464db66ec23bdd000001b19bb12224e0498057c7f90da667557f"
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # API endpoints
        self.weather_base_url = "http://api.weatherapi.com/v1"
        self.market_base_url = "https://api.marketstack.com/v1"
    
    def get_weather_data(self, location="Delhi", days=7):
        """Get weather forecast data"""
        try:
            url = f"{self.weather_base_url}/forecast.json"
            params = {
                'key': self.weather_api_key,
                'q': location,
                'days': days,
                'aqi': 'yes',
                'alerts': 'yes'
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Weather API Error: {e}")
            return self._get_mock_weather_data()
    
    def get_market_prices(self, crop_name="wheat", limit=10):
        """Get market prices for crops"""
        try:
            # Try different endpoints for market data
            endpoints = [
                f"{self.market_base_url}/tickers",
                f"{self.market_base_url}/eod",
                f"{self.market_base_url}/intraday"
            ]
            
            for endpoint in endpoints:
                try:
                    params = {
                        'access_key': self.market_api_key,
                        'symbols': crop_name.upper(),
                        'limit': limit
                    }
                    response = requests.get(endpoint, params=params, timeout=10)
                    response.raise_for_status()
                    data = response.json()
                    
                    if 'data' in data and data['data']:
                        return data
                        
                except Exception as e:
                    print(f"Market API endpoint {endpoint} failed: {e}")
                    continue
            
            # If all endpoints fail, return mock data
            return self._get_mock_market_data()
            
        except Exception as e:
            print(f"Market API Error: {e}")
            return self._get_mock_market_data()
    
    def get_gemini_response(self, prompt, max_tokens=500):
        """Get AI response from Gemini"""
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "I'm sorry, I'm having trouble connecting right now. Please try again later."
    
    def get_crop_recommendation(self, soil_data, weather_data, budget):
        """Get AI-powered crop recommendation"""
        prompt = f"""
        As an agricultural expert, analyze the following data and provide crop recommendations:
        
        Soil Data: {soil_data}
        Weather Forecast: {weather_data}
        Budget: ₹{budget}
        
        Please provide:
        1. Top 3 crop recommendations with reasons
        2. Expected yield per acre
        3. Required investment breakdown
        4. Risk assessment
        5. Best planting time
        6. Water requirements
        
        Format your response in a clear, actionable way for farmers.
        """
        return self.get_gemini_response(prompt)
    
    def get_financial_advice(self, farmer_query, financial_data=None):
        """Get financial literacy advice"""
        base_prompt = f"""
        You are a financial advisor specializing in agriculture. A farmer is asking: "{farmer_query}"
        
        Financial Context: {financial_data or "No specific financial data provided"}
        
        Please provide:
        1. Clear, simple explanation in Hindi/English mix
        2. Practical steps to take
        3. Government schemes that might help
        4. Loan options if applicable
        5. Risk mitigation strategies
        
        Keep the language simple and farmer-friendly.
        """
        return self.get_gemini_response(base_prompt)
    
    def get_pest_disease_advice(self, crop_name, symptoms, weather_conditions):
        """Get pest and disease management advice"""
        prompt = f"""
        As an agricultural expert, help with pest/disease management:
        
        Crop: {crop_name}
        Symptoms: {symptoms}
        Weather Conditions: {weather_conditions}
        
        Please provide:
        1. Likely pest/disease identification
        2. Immediate treatment options
        3. Prevention measures
        4. Cost-effective solutions
        5. When to contact agricultural officer
        
        Focus on organic and low-cost solutions first.
        """
        return self.get_gemini_response(prompt)
    
    def get_harvesting_advice(self, crop_name, weather_forecast, market_prices):
        """Get harvesting timing and selling advice"""
        prompt = f"""
        Help a farmer decide when to harvest and sell:
        
        Crop: {crop_name}
        Weather Forecast: {weather_forecast}
        Current Market Prices: {market_prices}
        
        Please advise:
        1. Optimal harvesting time
        2. Market timing for selling
        3. Storage recommendations if prices are low
        4. Price prediction for next 2-4 weeks
        5. Best marketplaces to sell
        
        Consider weather impact on crop quality and market demand.
        """
        return self.get_gemini_response(prompt)
    
    def _get_mock_weather_data(self):
        """Fallback weather data"""
        return {
            "location": {"name": "Delhi", "region": "Delhi"},
            "current": {
                "temp_c": 28,
                "condition": {"text": "Partly Cloudy"},
                "humidity": 65,
                "wind_kph": 12
            },
            "forecast": {
                "forecastday": [
                    {
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "day": {
                            "maxtemp_c": 32,
                            "mintemp_c": 22,
                            "condition": {"text": "Sunny"},
                            "daily_chance_of_rain": 10
                        }
                    }
                ]
            }
        }
    
    def _get_mock_market_data(self):
        """Fallback market data"""
        return {
            "data": [
                {
                    "symbol": "WHEAT",
                    "name": "Wheat",
                    "price": 2400,
                    "change_percent": 2.5
                },
                {
                    "symbol": "RICE", 
                    "name": "Rice",
                    "price": 3500,
                    "change_percent": -1.2
                }
            ]
        }

# Initialize the service
api_service = APIService()
