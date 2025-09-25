import json
from datetime import datetime, timedelta
from api_service import api_service
from ml_service import ml_service

class FarmingJourneyService:
    def __init__(self):
        self.api_service = api_service
        self.ml_service = ml_service
        self.farming_plans = {}  # Store farming plans
    
    def create_farming_plan(self, farmer_data):
        """Create a comprehensive farming plan from initial input"""
        try:
            # Generate unique plan ID
            plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get initial crop recommendation
            crop_recommendation = self.ml_service.predict_crop(farmer_data.get('soil_data', {}))
            
            # Get weather data for the location
            location = farmer_data.get('location', 'Delhi')
            weather_data = self.api_service.get_weather_data(location, 30)  # 30-day forecast
            
            # Get market prices for recommended crops
            market_data = {}
            for rec in crop_recommendation.get('recommendations', []):
                crop_name = rec['crop']
                market_data[crop_name] = self.api_service.get_market_prices(crop_name)
            
            # Create comprehensive farming plan
            farming_plan = {
                'plan_id': plan_id,
                'created_at': datetime.now().isoformat(),
                'farmer_data': farmer_data,
                'crop_recommendation': crop_recommendation,
                'weather_forecast': weather_data,
                'market_data': market_data,
                'timeline': self._generate_farming_timeline(farmer_data, crop_recommendation),
                'current_phase': 'planning',
                'reminders': [],
                'alerts': []
            }
            
            # Store the plan
            self.farming_plans[plan_id] = farming_plan
            
            # Generate initial reminders and alerts
            self._generate_reminders_and_alerts(farming_plan)
            
            return farming_plan
            
        except Exception as e:
            print(f"Error creating farming plan: {e}")
            return None
    
    def _generate_farming_timeline(self, farmer_data, crop_recommendation):
        """Generate detailed farming timeline based on crop and conditions"""
        best_crop = crop_recommendation.get('best_crop', 'wheat')
        location = farmer_data.get('location', 'Delhi')
        
        # Get AI advice for timeline
        ai_timeline_prompt = f"""
        Create a detailed farming timeline for {best_crop} cultivation in {location}.
        Consider the following factors:
        - Soil conditions: {farmer_data.get('soil_data', {})}
        - Budget: ₹{farmer_data.get('budget', 50000)}
        - Irrigation: {farmer_data.get('irrigation', 'rainfed')}
        
        Provide a week-by-week timeline including:
        1. Soil preparation
        2. Seed selection and treatment
        3. Planting schedule
        4. Fertilization schedule
        5. Irrigation schedule
        6. Pest monitoring
        7. Harvest timing
        8. Post-harvest activities
        
        Format as JSON with dates, activities, and important notes.
        """
        
        try:
            ai_timeline = self.api_service.get_gemini_response(ai_timeline_prompt)
            return self._parse_timeline_response(ai_timeline, best_crop)
        except Exception as e:
            print(f"Error generating AI timeline: {e}")
            return self._get_default_timeline(best_crop)
    
    def _parse_timeline_response(self, ai_response, crop):
        """Parse AI timeline response into structured format"""
        # This would parse the AI response into structured timeline
        # For now, return a default timeline
        return self._get_default_timeline(crop)
    
    def _get_default_timeline(self, crop):
        """Get default farming timeline based on crop type"""
        timelines = {
            'wheat': {
                'weeks': [
                    {'week': 1, 'phase': 'Soil Preparation', 'activities': ['Land plowing', 'Soil testing', 'pH adjustment'], 'duration': '1-2 weeks'},
                    {'week': 2, 'phase': 'Seed Preparation', 'activities': ['Seed selection', 'Seed treatment', 'Seed bed preparation'], 'duration': '1 week'},
                    {'week': 3, 'phase': 'Planting', 'activities': ['Sowing', 'Seed covering', 'Initial irrigation'], 'duration': '1-2 weeks'},
                    {'week': 6, 'phase': 'Growth Monitoring', 'activities': ['Germination check', 'Weed control', 'First fertilization'], 'duration': '2-3 weeks'},
                    {'week': 10, 'phase': 'Active Growth', 'activities': ['Regular irrigation', 'Pest monitoring', 'Second fertilization'], 'duration': '4-6 weeks'},
                    {'week': 16, 'phase': 'Pre-Harvest', 'activities': ['Final irrigation', 'Disease check', 'Harvest planning'], 'duration': '2-3 weeks'},
                    {'week': 18, 'phase': 'Harvesting', 'activities': ['Harvest', 'Threshing', 'Storage preparation'], 'duration': '1-2 weeks'},
                    {'week': 20, 'phase': 'Post-Harvest', 'activities': ['Storage', 'Market preparation', 'Record keeping'], 'duration': '2-4 weeks'}
                ]
            },
            'rice': {
                'weeks': [
                    {'week': 1, 'phase': 'Seedbed Preparation', 'activities': ['Nursery preparation', 'Seed selection', 'Seed treatment'], 'duration': '1 week'},
                    {'week': 2, 'phase': 'Nursery Management', 'activities': ['Seed sowing', 'Water management', 'Fertilizer application'], 'duration': '3-4 weeks'},
                    {'week': 5, 'phase': 'Field Preparation', 'activities': ['Land preparation', 'Puddling', 'Leveling'], 'duration': '1-2 weeks'},
                    {'week': 6, 'phase': 'Transplanting', 'activities': ['Seedling uprooting', 'Transplanting', 'Water management'], 'duration': '1 week'},
                    {'week': 8, 'phase': 'Early Growth', 'activities': ['Gap filling', 'Weed control', 'First fertilization'], 'duration': '2-3 weeks'},
                    {'week': 12, 'phase': 'Active Growth', 'activities': ['Tillage', 'Fertilizer application', 'Pest monitoring'], 'duration': '4-6 weeks'},
                    {'week': 18, 'phase': 'Pre-Harvest', 'activities': ['Water drainage', 'Disease monitoring', 'Harvest preparation'], 'duration': '2-3 weeks'},
                    {'week': 20, 'phase': 'Harvesting', 'activities': ['Harvest', 'Threshing', 'Drying'], 'duration': '1-2 weeks'}
                ]
            }
        }
        
        return timelines.get(crop.lower(), timelines['wheat'])
    
    def _generate_reminders_and_alerts(self, farming_plan):
        """Generate reminders and alerts based on farming plan"""
        reminders = []
        alerts = []
        
        # Weather-based alerts
        weather = farming_plan.get('weather_forecast', {})
        if weather.get('forecast'):
            for day in weather['forecast'].get('forecastday', [])[:7]:  # Next 7 days
                if day.get('day', {}).get('daily_chance_of_rain', 0) > 70:
                    alerts.append({
                        'type': 'rain_alert',
                        'message': f"High chance of rain ({day['day']['daily_chance_of_rain']}%) on {day['date']}. Consider protecting your crops.",
                        'date': day['date'],
                        'priority': 'high'
                    })
        
        # Timeline-based reminders
        timeline = farming_plan.get('timeline', {})
        current_phase = farming_plan.get('current_phase', 'planning')
        
        for week_data in timeline.get('weeks', []):
            if week_data.get('phase') == current_phase:
                for activity in week_data.get('activities', []):
                    reminders.append({
                        'type': 'activity_reminder',
                        'message': f"Time to {activity.lower()}",
                        'activity': activity,
                        'phase': week_data.get('phase'),
                        'priority': 'medium'
                    })
        
        # Market-based alerts
        market_data = farming_plan.get('market_data', {})
        for crop, data in market_data.items():
            if data and 'data' in data and data['data']:
                price_change = data['data'][0].get('change_percent', 0)
                if abs(price_change) > 5:  # Significant price change
                    alerts.append({
                        'type': 'market_alert',
                        'message': f"{crop} prices changed by {price_change}%. Consider timing your harvest/sale.",
                        'crop': crop,
                        'change': price_change,
                        'priority': 'medium'
                    })
        
        farming_plan['reminders'] = reminders
        farming_plan['alerts'] = alerts
    
    def update_farming_progress(self, plan_id, progress_update):
        """Update farming progress and generate new recommendations"""
        if plan_id not in self.farming_plans:
            return None
        
        plan = self.farming_plans[plan_id]
        plan['last_updated'] = datetime.now().isoformat()
        plan['progress_updates'] = plan.get('progress_updates', [])
        plan['progress_updates'].append(progress_update)
        
        # Update current phase based on progress
        if progress_update.get('phase_completed'):
            current_phase_index = self._get_phase_index(plan['current_phase'], plan['timeline'])
            if current_phase_index < len(plan['timeline']['weeks']) - 1:
                plan['current_phase'] = plan['timeline']['weeks'][current_phase_index + 1]['phase']
        
        # Regenerate reminders and alerts
        self._generate_reminders_and_alerts(plan)
        
        return plan
    
    def get_farming_dashboard(self, plan_id):
        """Get comprehensive farming dashboard data"""
        if plan_id not in self.farming_plans:
            return None
        
        plan = self.farming_plans[plan_id]
        
        # Get current weather
        location = plan['farmer_data'].get('location', 'Delhi')
        current_weather = self.api_service.get_weather_data(location, 1)
        
        # Get current market prices
        best_crop = plan['crop_recommendation'].get('best_crop', 'wheat')
        current_market = self.api_service.get_market_prices(best_crop)
        
        # Get price prediction
        price_prediction = self.ml_service.predict_prices(best_crop, 30)
        
        dashboard_data = {
            'plan_id': plan_id,
            'current_phase': plan['current_phase'],
            'current_weather': current_weather,
            'current_market': current_market,
            'price_prediction': price_prediction,
            'active_reminders': [r for r in plan['reminders'] if r.get('priority') == 'high'],
            'active_alerts': [a for a in plan['alerts'] if a.get('priority') == 'high'],
            'timeline': plan['timeline'],
            'next_activities': self._get_next_activities(plan),
            'crop_health_score': self._calculate_crop_health_score(plan),
            'financial_summary': self._calculate_financial_summary(plan)
        }
        
        return dashboard_data
    
    def _get_phase_index(self, phase, timeline):
        """Get index of current phase in timeline"""
        for i, week_data in enumerate(timeline.get('weeks', [])):
            if week_data.get('phase') == phase:
                return i
        return 0
    
    def _get_next_activities(self, plan):
        """Get next activities based on current phase"""
        timeline = plan.get('timeline', {})
        current_phase = plan.get('current_phase', 'planning')
        
        for week_data in timeline.get('weeks', []):
            if week_data.get('phase') == current_phase:
                return week_data.get('activities', [])
        return []
    
    def _calculate_crop_health_score(self, plan):
        """Calculate overall crop health score"""
        # This would integrate with weather, pest alerts, etc.
        # For now, return a mock score
        return {
            'score': 85,
            'status': 'Good',
            'factors': ['Weather favorable', 'No pest alerts', 'Growth on track']
        }
    
    def _calculate_financial_summary(self, plan):
        """Calculate financial summary"""
        budget = plan['farmer_data'].get('budget', 50000)
        best_crop = plan['crop_recommendation'].get('best_crop', 'wheat')
        
        # Get price prediction for ROI calculation
        price_prediction = self.ml_service.predict_prices(best_crop, 30)
        
        estimated_yield = 2.5  # tons per acre (mock data)
        land_size = plan['farmer_data'].get('soil_data', {}).get('land_size', 2)
        
        return {
            'total_budget': budget,
            'estimated_yield': f"{estimated_yield * land_size} tons",
            'estimated_income': f"₹{price_prediction.get('future_price', 2400) * estimated_yield * land_size * 10}",
            'roi_percentage': 25.5,  # Mock calculation
            'market_trend': price_prediction.get('trend_percentage', 0)
        }

# Initialize the service
farming_journey_service = FarmingJourneyService()

