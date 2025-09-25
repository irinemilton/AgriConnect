import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import json
import os

class MLService:
    def __init__(self):
        self.models_dir = "models"
        self.crop_recommender = None
        self.price_forecaster = None
        self.label_encoders = {}
        
        # Load or create models
        self._load_or_create_models()
    
    def _load_or_create_models(self):
        """Load existing models or create new ones"""
        try:
            # Try to load existing models
            self.crop_recommender = joblib.load(f"{self.models_dir}/crop_recommender.pkl")
            self.price_forecaster = joblib.load(f"{self.models_dir}/price_forecaster.pkl")
            print("Models loaded successfully")
        except:
            print("Creating new models...")
            self._create_crop_recommender()
            self._create_price_forecaster()
    
    def _create_crop_recommender(self):
        """Create crop recommendation model"""
        # Sample agricultural data for training
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'soil_type': np.random.choice(['clay', 'sandy', 'loamy', 'silty'], n_samples),
            'soil_ph': np.random.normal(6.5, 1.0, n_samples),
            'rainfall': np.random.normal(800, 200, n_samples),
            'temperature': np.random.normal(28, 5, n_samples),
            'humidity': np.random.normal(70, 10, n_samples),
            'nitrogen': np.random.normal(50, 15, n_samples),
            'phosphorus': np.random.normal(30, 10, n_samples),
            'potassium': np.random.normal(40, 12, n_samples),
            'budget': np.random.normal(50000, 15000, n_samples),
            'land_size': np.random.normal(2, 1, n_samples)
        }
        
        # Define crop recommendations based on conditions
        crops = []
        for i in range(n_samples):
            soil = data['soil_type'][i]
            ph = data['soil_ph'][i]
            temp = data['temperature'][i]
            rainfall = data['rainfall'][i]
            budget = data['budget'][i]
            
            if soil == 'loamy' and 6 <= ph <= 7.5 and temp > 25:
                if rainfall > 700 and budget > 40000:
                    crops.append('rice')
                elif rainfall < 600 and budget > 30000:
                    crops.append('wheat')
                else:
                    crops.append('maize')
            elif soil == 'sandy' and temp > 30:
                crops.append('cotton')
            elif soil == 'clay' and ph > 7:
                crops.append('sugarcane')
            else:
                crops.append('vegetables')
        
        data['crop'] = crops
        
        # Prepare features
        df = pd.DataFrame(data)
        X = df.drop('crop', axis=1)
        y = df['crop']
        
        # Encode categorical variables
        le_soil = LabelEncoder()
        X['soil_type'] = le_soil.fit_transform(X['soil_type'])
        self.label_encoders['soil_type'] = le_soil
        
        # Train model
        self.crop_recommender = RandomForestClassifier(n_estimators=100, random_state=42)
        self.crop_recommender.fit(X, y)
        
        # Save model
        os.makedirs(self.models_dir, exist_ok=True)
        joblib.dump(self.crop_recommender, f"{self.models_dir}/crop_recommender.pkl")
        joblib.dump(self.label_encoders, f"{self.models_dir}/label_encoders.pkl")
    
    def _create_price_forecaster(self):
        """Create price forecasting model"""
        # Sample price data
        np.random.seed(42)
        dates = pd.date_range(start='2020-01-01', end='2024-01-01', freq='D')
        
        crops = ['wheat', 'rice', 'maize', 'cotton', 'sugarcane']
        price_data = []
        
        for crop in crops:
            base_price = {'wheat': 2400, 'rice': 3500, 'maize': 1800, 'cotton': 6000, 'sugarcane': 3200}[crop]
            
            for date in dates:
                # Seasonal variation
                month = date.month
                seasonal_factor = 1 + 0.2 * np.sin(2 * np.pi * month / 12)
                
                # Random variation
                random_factor = np.random.normal(1, 0.1)
                
                price = base_price * seasonal_factor * random_factor
                
                price_data.append({
                    'date': date,
                    'crop': crop,
                    'price': price,
                    'month': month,
                    'year': date.year
                })
        
        df = pd.DataFrame(price_data)
        
        # Prepare features for forecasting
        features = ['month', 'year']
        X = df[features]
        y = df['price']
        
        # Train model
        self.price_forecaster = RandomForestRegressor(n_estimators=100, random_state=42)
        self.price_forecaster.fit(X, y)
        
        # Save model
        joblib.dump(self.price_forecaster, f"{self.models_dir}/price_forecaster.pkl")
    
    def predict_crop(self, soil_data):
        """Predict best crop based on soil and weather conditions"""
        try:
            # Prepare input data
            input_data = pd.DataFrame([{
                'soil_type': soil_data.get('soil_type', 'loamy'),
                'soil_ph': soil_data.get('soil_ph', 6.5),
                'rainfall': soil_data.get('rainfall', 800),
                'temperature': soil_data.get('temperature', 28),
                'humidity': soil_data.get('humidity', 70),
                'nitrogen': soil_data.get('nitrogen', 50),
                'phosphorus': soil_data.get('phosphorus', 30),
                'potassium': soil_data.get('potassium', 40),
                'budget': soil_data.get('budget', 50000),
                'land_size': soil_data.get('land_size', 2)
            }])
            
            # Encode categorical variables
            input_data['soil_type'] = self.label_encoders['soil_type'].transform(input_data['soil_type'])
            
            # Make prediction
            prediction = self.crop_recommender.predict(input_data)[0]
            probabilities = self.crop_recommender.predict_proba(input_data)[0]
            classes = self.crop_recommender.classes_
            
            # Get top 3 recommendations
            top_indices = np.argsort(probabilities)[-3:][::-1]
            recommendations = []
            
            for idx in top_indices:
                recommendations.append({
                    'crop': classes[idx],
                    'confidence': float(probabilities[idx]),
                    'estimated_yield': self._estimate_yield(classes[idx], soil_data),
                    'required_investment': self._estimate_investment(classes[idx], soil_data)
                })
            
            return {
                'recommendations': recommendations,
                'best_crop': prediction,
                'confidence': float(max(probabilities))
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {
                'recommendations': [
                    {'crop': 'wheat', 'confidence': 0.8, 'estimated_yield': '2-3 tons/acre', 'required_investment': '₹40,000-50,000'},
                    {'crop': 'rice', 'confidence': 0.7, 'estimated_yield': '3-4 tons/acre', 'required_investment': '₹45,000-60,000'},
                    {'crop': 'maize', 'confidence': 0.6, 'estimated_yield': '2-3 tons/acre', 'required_investment': '₹35,000-45,000'}
                ],
                'best_crop': 'wheat',
                'confidence': 0.8
            }
    
    def predict_prices(self, crop_name, days_ahead=30):
        """Predict crop prices for next N days"""
        try:
            future_dates = pd.date_range(start=datetime.now(), periods=days_ahead, freq='D')
            predictions = []
            
            for date in future_dates:
                features = pd.DataFrame([{
                    'month': date.month,
                    'year': date.year
                }])
                
                price = self.price_forecaster.predict(features)[0]
                
                # Add crop-specific adjustments
                crop_multipliers = {
                    'wheat': 1.0,
                    'rice': 1.46,
                    'maize': 0.75,
                    'cotton': 2.5,
                    'sugarcane': 1.33
                }
                
                adjusted_price = price * crop_multipliers.get(crop_name.lower(), 1.0)
                
                predictions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'price': round(adjusted_price, 2),
                    'trend': 'increasing' if len(predictions) > 0 and adjusted_price > predictions[-1]['price'] else 'decreasing'
                })
            
            # Calculate overall trend
            if len(predictions) > 1:
                start_price = predictions[0]['price']
                end_price = predictions[-1]['price']
                trend_percentage = ((end_price - start_price) / start_price) * 100
            else:
                trend_percentage = 0
            
            return {
                'predictions': predictions,
                'current_price': predictions[0]['price'] if predictions else 0,
                'future_price': predictions[-1]['price'] if predictions else 0,
                'trend_percentage': round(trend_percentage, 2),
                'recommendation': self._get_selling_recommendation(trend_percentage)
            }
            
        except Exception as e:
            print(f"Price prediction error: {e}")
            return {
                'predictions': [],
                'current_price': 2400,
                'future_price': 2450,
                'trend_percentage': 2.08,
                'recommendation': 'Prices are rising slightly. Consider waiting a bit longer.'
            }
    
    def _estimate_yield(self, crop, soil_data):
        """Estimate crop yield based on conditions"""
        base_yields = {
            'wheat': '2-3 tons/acre',
            'rice': '3-4 tons/acre',
            'maize': '2-3 tons/acre',
            'cotton': '1-2 tons/acre',
            'sugarcane': '60-80 tons/acre',
            'vegetables': '15-25 tons/acre'
        }
        return base_yields.get(crop, '2-3 tons/acre')
    
    def _estimate_investment(self, crop, soil_data):
        """Estimate required investment"""
        base_investments = {
            'wheat': '₹40,000-50,000',
            'rice': '₹45,000-60,000',
            'maize': '₹35,000-45,000',
            'cotton': '₹50,000-70,000',
            'sugarcane': '₹60,000-80,000',
            'vegetables': '₹30,000-50,000'
        }
        return base_investments.get(crop, '₹40,000-50,000')
    
    def _get_selling_recommendation(self, trend_percentage):
        """Get selling recommendation based on price trend"""
        if trend_percentage > 5:
            return "Prices are rising significantly. Consider selling soon to maximize profit."
        elif trend_percentage > 0:
            return "Prices are rising slightly. You can wait a bit longer or sell now."
        elif trend_percentage > -5:
            return "Prices are stable. Sell when convenient for you."
        else:
            return "Prices are declining. Consider selling soon to avoid further losses."

# Initialize the service
ml_service = MLService()

