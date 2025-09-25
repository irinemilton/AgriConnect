import requests
import yfinance as yf
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
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "8ec8aac1ced747ec89655941252409")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBIA0VRcgOtGImuIa2HSIaAcLAyxM6UYM4")
        self.market_api_key = os.getenv("MARKET_API_KEY", "579b464db66ec23bdd000001b19bb12224e0498057c7f90da667557f")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # API endpoints
        self.weather_base_url = "https://api.weatherapi.com/v1"
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
                    
                    # Normalize to a consistent structure expected by templates
                    normalized = self._normalize_marketstack_response(data)
                    if normalized.get('data'):
                        return normalized
                        
                except Exception as e:
                    print(f"Market API endpoint {endpoint} failed: {e}")
                    continue
            
            # If all endpoints fail, return mock data
            yahoo = self._get_yahoo_prices(crop_name)
            if yahoo.get('data'):
                return yahoo
            return self._get_mock_market_data()
            
        except Exception as e:
            print(f"Market API Error: {e}")
            yahoo = self._get_yahoo_prices(crop_name)
            if yahoo.get('data'):
                return yahoo
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

    def _normalize_marketstack_response(self, raw: dict) -> dict:
        """Convert Marketstack responses (tickers/eod/intraday) into a unified data list.
        Each item has: symbol, name, price, change_percent (if available).
        """
        try:
            items = []
            if not isinstance(raw, dict):
                return {"data": items}

            # EOD / Intraday: raw.get('data') is a list of quotes
            if isinstance(raw.get('data'), list) and raw['data']:
                for entry in raw['data']:
                    symbol = entry.get('symbol') or entry.get('ticker') or 'UNKNOWN'
                    name = entry.get('name') or symbol
                    # Prefer close price for eod; last/price for intraday
                    price = entry.get('close') or entry.get('last') or entry.get('price') or 0
                    change = entry.get('change_percent') or entry.get('percent_change') or 0
                    items.append({
                        'symbol': symbol,
                        'name': name,
                        'price': round(price, 2) if isinstance(price, (int, float)) else price,
                        'change_percent': change or 0
                    })
                return {"data": items}

            # Tickers endpoint: synthesize items with placeholder price
            if isinstance(raw.get('data'), dict) or isinstance(raw.get('data'), list):
                data_block = raw.get('data')
                if isinstance(data_block, list):
                    for t in data_block:
                        symbol = t.get('symbol') or t.get('ticker') or 'UNKNOWN'
                        name = t.get('name') or symbol
                        items.append({'symbol': symbol, 'name': name, 'price': 0, 'change_percent': 0})
                    return {"data": items}

        except Exception as e:
            print(f"Normalization error: {e}")
        return {"data": []}

    def _get_yahoo_prices(self, crop_name: str) -> dict:
        """Fallback to Yahoo Finance for representative commodity proxies.
        Maps crop names to finance tickers and returns a normalized structure.
        """
        mapping = {
            'wheat': 'ZW=F',       # CBOT Wheat Futures
            'rice': 'ZR=F',        # Rough Rice Futures
            'maize': 'ZC=F',       # Corn Futures
            'corn': 'ZC=F',
            'cotton': 'CT=F',      # Cotton Futures
            'sugarcane': 'SB=F',   # Sugar No.11 Futures (proxy)
        }
        ticker_symbol = mapping.get(crop_name.lower())
        if not ticker_symbol:
            return {"data": []}
        try:
            t = yf.Ticker(ticker_symbol)
            info = t.fast_info if hasattr(t, 'fast_info') else {}
            last_price = getattr(t, 'history')(period='1d')
            price = float(info.get('last_price') or (last_price['Close'][-1] if not last_price.empty else 0))
            change = 0
            return {"data": [{
                'symbol': ticker_symbol,
                'name': crop_name.capitalize(),
                'price': round(price, 2),
                'change_percent': change
            }]}
        except Exception as e:
            print(f"Yahoo fallback error: {e}")
            return {"data": []}

# Initialize the service
api_service = APIService()
