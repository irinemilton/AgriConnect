from flask import current_app
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, FarmingPlan, Notification, ChatMessage
from datetime import datetime
import json

class AuthService:
    def __init__(self):
        pass
    
    def register_user(self, username, email, password, full_name, phone=None, location=None):
        """Register a new user"""
        try:
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                return {'success': False, 'error': 'Username already exists'}
            
            if User.query.filter_by(email=email).first():
                return {'success': False, 'error': 'Email already registered'}
            
            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone,
                location=location
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            # Create welcome notification
            welcome_notification = Notification(
                user_id=user.id,
                title="Welcome to AgriConnect!",
                message="Your account has been created successfully. Start your farming journey now!",
                notification_type="welcome",
                priority="medium"
            )
            db.session.add(welcome_notification)
            db.session.commit()
            
            return {'success': True, 'user': user.to_dict()}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def login_user(self, username, password):
        """Login user"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    return {'success': False, 'error': 'Account is deactivated'}
                
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Login user
                login_user(user)
                
                return {'success': True, 'user': user.to_dict()}
            else:
                return {'success': False, 'error': 'Invalid username or password'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def logout_user(self):
        """Logout current user"""
        try:
            logout_user()
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_profile(self, user_id):
        """Get user profile"""
        try:
            user = User.query.get(user_id)
            if user:
                return {'success': True, 'user': user.to_dict()}
            else:
                return {'success': False, 'error': 'User not found'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_user_profile(self, user_id, **kwargs):
        """Update user profile"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {'success': False, 'error': 'User not found'}
            
            # Update allowed fields
            allowed_fields = ['full_name', 'email', 'phone', 'location']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(user, field, value)
            
            db.session.commit()
            return {'success': True, 'user': user.to_dict()}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def create_farming_plan(self, user_id, farm_data):
        """Create farming plan for user"""
        try:
            # Generate unique plan ID
            plan_id = f"plan_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create farming plan
            farming_plan = FarmingPlan(
                plan_id=plan_id,
                user_id=user_id,
                location=farm_data.get('location'),
                land_size=farm_data.get('landSize'),
                soil_type=farm_data.get('soil_data', {}).get('soil_type'),
                soil_ph=farm_data.get('soil_data', {}).get('soil_ph'),
                nitrogen=farm_data.get('soil_data', {}).get('nitrogen'),
                phosphorus=farm_data.get('soil_data', {}).get('phosphorus'),
                potassium=farm_data.get('soil_data', {}).get('potassium'),
                rainfall=farm_data.get('soil_data', {}).get('rainfall'),
                temperature=farm_data.get('soil_data', {}).get('temperature'),
                humidity=farm_data.get('soil_data', {}).get('humidity'),
                irrigation=farm_data.get('irrigation'),
                budget=farm_data.get('budget'),
                experience=farm_data.get('experience'),
                goal=farm_data.get('goal')
            )
            
            db.session.add(farming_plan)
            db.session.commit()
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                title="Farming Plan Created!",
                message=f"Your farming plan {plan_id} has been created successfully. AI recommendations are being generated.",
                notification_type="plan_created",
                priority="high"
            )
            db.session.add(notification)
            db.session.commit()
            
            return {'success': True, 'plan_id': plan_id, 'farming_plan': farming_plan.to_dict()}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_farming_plans(self, user_id):
        """Get all farming plans for user"""
        try:
            plans = FarmingPlan.query.filter_by(user_id=user_id).order_by(FarmingPlan.created_at.desc()).all()
            return {'success': True, 'plans': [plan.to_dict() for plan in plans]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_user_notifications(self, user_id, unread_only=False):
        """Get user notifications"""
        try:
            query = Notification.query.filter_by(user_id=user_id)
            if unread_only:
                query = query.filter_by(is_read=False)
            
            notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
            return {'success': True, 'notifications': [notif.to_dict() for notif in notifications]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def mark_notification_read(self, notification_id, user_id):
        """Mark notification as read"""
        try:
            notification = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Notification not found'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def create_notification(self, user_id, title, message, notification_type='general', priority='medium'):
        """Create notification for user"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority
            )
            db.session.add(notification)
            db.session.commit()
            return {'success': True, 'notification': notification.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def save_chat_message(self, user_id, message, response=None, message_type='general'):
        """Save chat message"""
        try:
            chat_message = ChatMessage(
                user_id=user_id,
                message=message,
                response=response,
                message_type=message_type
            )
            db.session.add(chat_message)
            db.session.commit()
            return {'success': True, 'chat_message': chat_message.to_dict()}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_chat_history(self, user_id, limit=50):
        """Get user chat history"""
        try:
            messages = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.desc()).limit(limit).all()
            return {'success': True, 'messages': [msg.to_dict() for msg in messages]}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize the service
auth_service = AuthService()



