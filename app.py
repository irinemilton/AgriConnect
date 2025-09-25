from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from werkzeug.security import check_password_hash
import json
from datetime import datetime, timedelta
import sys
import os

# Import database and models
from models import db, User
from config import Config

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

try:
    from api_service import api_service
    from ml_service import ml_service
    from farming_journey_service import farming_journey_service
    from auth_service import auth_service
except ImportError as e:
    print(f"Import error: {e}")
    # Create mock services for development
    class MockAPIService:
        def get_weather_data(self, location="Delhi", days=7):
            return {
                "location": {"name": "Delhi", "region": "Delhi"},
                "current": {"temp_c": 28, "condition": {"text": "Partly Cloudy"}},
                "forecast": {"forecastday": []}
            }
        
        def get_market_prices(self, crop_name="wheat"):
            return {"data": [{"symbol": "WHEAT", "name": "Wheat", "price": 2400}]}
        
        def get_gemini_response(self, prompt):
            return "AI response would be here"
        
        def get_crop_recommendation(self, soil_data, weather_data, budget):
            return "Crop recommendations would be here"
        
        def get_financial_advice(self, farmer_query, financial_data=None):
            return "Financial advice would be here"
    
    class MockMLService:
        def predict_crop(self, soil_data):
            return {
                'recommendations': [
                    {'crop': 'wheat', 'confidence': 0.8, 'estimated_yield': '2-3 tons/acre', 'required_investment': '₹40,000-50,000'}
                ],
                'best_crop': 'wheat',
                'confidence': 0.8
            }
        
        def predict_prices(self, crop_name, days_ahead=30):
            return {
                'predictions': [],
                'current_price': 2400,
                'future_price': 2450,
                'trend_percentage': 2.08,
                'recommendation': 'Prices are rising slightly.'
            }
    
    api_service = MockAPIService()
    ml_service = MockMLService()
    
    class MockFarmingJourneyService:
        def create_farming_plan(self, farmer_data):
            return {
                'plan_id': 'mock_plan_123',
                'created_at': datetime.now().isoformat(),
                'farmer_data': farmer_data,
                'crop_recommendation': {'best_crop': 'wheat', 'recommendations': []},
                'current_phase': 'planning'
            }
        
        def get_farming_dashboard(self, plan_id):
            return {
                'current_phase': 'planning',
                'current_weather': {'current': {'temp_c': 28, 'condition': {'text': 'Sunny'}}},
                'active_alerts': [],
                'active_reminders': []
            }
    
    farming_journey_service = MockFarmingJourneyService()
    
    class MockAuthService:
        def register_user(self, **kwargs):
            return {'success': False, 'error': 'Auth service not available'}
        def login_user(self, username, password):
            return {'success': False, 'error': 'Auth service not available'}
    
    auth_service = MockAuthService()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
CORS(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Database error: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('farming_journey.html')

@app.route('/farming-journey')
@login_required
def farming_journey():
    return render_template('farming_journey.html')

@app.route('/crop-recommendation')
def crop_recommendation():
    return render_template('crop_recommendation.html')

@app.route('/weather')
def weather():
    location = request.args.get('location', 'Delhi')
    weather_data = api_service.get_weather_data(location)
    return render_template('weather.html', weather=weather_data)

@app.route('/marketplace')
def marketplace():
    crop = request.args.get('crop', 'wheat')
    market_data = api_service.get_market_prices(crop)
    
    # Format market data for template
    formatted_markets = []
    if 'data' in market_data:
        for item in market_data['data']:
            formatted_markets.append({
                'crop': item.get('name', 'Unknown'),
                'price': f"₹{item.get('price', 0)}/quintal",
                'change': item.get('change_percent', 0)
            })
    
    return render_template('marketplace.html', markets=formatted_markets)

# API Endpoints
@app.route('/api/crop-recommendation', methods=['POST'])
def api_crop_recommendation():
    try:
        data = request.json
        soil_data = data.get('soil_data', {})
        budget = data.get('budget', 50000)
        
        # Get weather data for the location
        location = data.get('location', 'Delhi')
        weather_data = api_service.get_weather_data(location)
        
        # Get ML prediction
        ml_result = ml_service.predict_crop(soil_data)
        
        # Get AI recommendation
        ai_recommendation = api_service.get_crop_recommendation(soil_data, weather_data, budget)
        
        return jsonify({
            'success': True,
            'ml_recommendations': ml_result,
            'ai_advice': ai_recommendation,
            'weather_context': weather_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/price-prediction', methods=['POST'])
def api_price_prediction():
    try:
        data = request.json
        crop_name = data.get('crop', 'wheat')
        days_ahead = data.get('days_ahead', 30)
        
        # Get ML prediction
        price_prediction = ml_service.predict_prices(crop_name, days_ahead)
        
        # Get current market data
        market_data = api_service.get_market_prices(crop_name)
        
        return jsonify({
            'success': True,
            'predictions': price_prediction,
            'current_market': market_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/financial-advice', methods=['POST'])
def api_financial_advice():
    try:
        data = request.json
        query = data.get('query', '')
        financial_data = data.get('financial_data', {})
        
        advice = api_service.get_financial_advice(query, financial_data)
        
        return jsonify({
            'success': True,
            'advice': advice
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/pest-disease-advice', methods=['POST'])
def api_pest_disease_advice():
    try:
        data = request.json
        crop_name = data.get('crop', '')
        symptoms = data.get('symptoms', '')
        weather_conditions = data.get('weather_conditions', '')
        
        advice = api_service.get_pest_disease_advice(crop_name, symptoms, weather_conditions)
        
        return jsonify({
            'success': True,
            'advice': advice
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/harvesting-advice', methods=['POST'])
def api_harvesting_advice():
    try:
        data = request.json
        crop_name = data.get('crop', '')
        
        # Get weather forecast
        location = data.get('location', 'Delhi')
        weather_forecast = api_service.get_weather_data(location)
        
        # Get market prices
        market_prices = api_service.get_market_prices(crop_name)
        
        # Get price prediction
        price_prediction = ml_service.predict_prices(crop_name, 30)
        
        # Get AI advice
        advice = api_service.get_harvesting_advice(crop_name, weather_forecast, market_prices)
        
        return jsonify({
            'success': True,
            'advice': advice,
            'price_prediction': price_prediction,
            'weather_forecast': weather_forecast
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/weather', methods=['GET'])
def api_weather():
    try:
        location = request.args.get('location', 'Delhi')
        days = int(request.args.get('days', 7))
        
        weather_data = api_service.get_weather_data(location, days)
        
        return jsonify({
            'success': True,
            'weather': weather_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/market-prices', methods=['GET'])
def api_market_prices():
    try:
        crop = request.args.get('crop', 'wheat')
        
        market_data = api_service.get_market_prices(crop)
        
        return jsonify({
            'success': True,
            'market_data': market_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/start-farming-journey', methods=['POST'])
def api_start_farming_journey():
    try:
        farmer_data = request.json
        
        # Create farming plan
        farming_plan = farming_journey_service.create_farming_plan(farmer_data)
        
        if farming_plan:
            return jsonify({
                'success': True,
                'plan_id': farming_plan['plan_id'],
                'message': 'Farming journey started successfully!',
                'farming_plan': farming_plan
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create farming plan'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/farming-dashboard/<plan_id>')
def api_farming_dashboard(plan_id):
    try:
        dashboard_data = farming_journey_service.get_farming_dashboard(plan_id)
        
        if dashboard_data:
            return jsonify({
                'success': True,
                'dashboard': dashboard_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Farming plan not found'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/update-progress/<plan_id>', methods=['POST'])
def api_update_progress(plan_id):
    try:
        progress_update = request.json
        
        # Update farming progress
        updated_plan = farming_journey_service.update_farming_progress(plan_id, progress_update)
        
        if updated_plan:
            return jsonify({
                'success': True,
                'message': 'Progress updated successfully!',
                'plan': updated_plan
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update progress'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get-reminders/<plan_id>')
def api_get_reminders(plan_id):
    try:
        dashboard_data = farming_journey_service.get_farming_dashboard(plan_id)
        
        if dashboard_data:
            reminders = dashboard_data.get('active_reminders', [])
            alerts = dashboard_data.get('active_alerts', [])
            
            return jsonify({
                'success': True,
                'reminders': reminders,
                'alerts': alerts
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Farming plan not found'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Authentication API endpoints
@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        result = auth_service.register_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            full_name=data.get('fullName'),
            phone=data.get('phone'),
            location=data.get('location')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        result = auth_service.login_user(
            username=data.get('username'),
            password=data.get('password')
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/profile')
@login_required
def api_user_profile():
    try:
        result = auth_service.get_user_profile(current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications')
@login_required
def api_notifications():
    try:
        result = auth_service.get_user_notifications(current_user.id)
        if result['success']:
            unread_count = len([n for n in result['notifications'] if not n['is_read']])
            result['unread_count'] = unread_count
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def api_mark_notification_read(notification_id):
    try:
        result = auth_service.mark_notification_read(notification_id, current_user.id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/test')
def api_test():
    return jsonify({'message': 'AI AgriConnect API is working!', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True)