# 🌱 AgriConnect - AI-Powered Smart Farming Platform

## 🚀 Overview

AgriConnect is a comprehensive AI-powered agricultural platform that guides farmers through the entire farming lifecycle - from planning and planting to harvesting and selling. Built with cutting-edge Machine Learning and AI technologies, it provides personalized recommendations, real-time weather insights, market predictions, and financial guidance.

## ✨ Key Features

### 🤖 AI Crop Doctor
- **Machine Learning Crop Recommendations**: Uses Random Forest algorithms to predict the best crops based on soil analysis, weather conditions, and budget
- **AI-Powered Expert Advice**: Integrates Google Gemini AI for personalized farming guidance
- **Comprehensive Soil Analysis**: Considers pH levels, nutrient content (N-P-K), and soil type
- **Yield Predictions**: Estimates crop yields and required investments

### 🌤️ Hyperlocal Weather Intelligence
- **Real-time Weather Data**: Integration with WeatherAPI for accurate local forecasts
- **Pest & Disease Alerts**: AI-powered early warning system for pest outbreaks
- **Irrigation Recommendations**: Smart water management based on weather patterns
- **Risk Assessment**: Weather-based farming risk evaluation

### 📈 Smart Marketplace
- **AI Price Predictions**: Machine Learning models predict crop prices for next 30 days
- **Optimal Selling Timing**: Recommendations on when to sell for maximum profit
- **Market Trend Analysis**: Real-time market data integration
- **Buyer Connections**: Direct marketplace for farmers and buyers

### 💰 Financial AI Advisor
- **Gemini AI Chatbot**: Personalized financial advice for loans, subsidies, and investments
- **Loan Eligibility Assessment**: AI-powered loan recommendation system
- **Government Scheme Guidance**: Information about available agricultural schemes
- **Investment Planning**: Budget optimization and ROI calculations

### 🐛 Pest & Disease Monitor
- **AI Diagnosis**: Symptom-based pest and disease identification
- **Organic Treatment Plans**: Eco-friendly solution recommendations
- **Prevention Strategies**: Proactive pest management advice
- **Cost-effective Solutions**: Low-cost treatment options

### 🌾 Harvest Optimizer
- **Smart Harvest Timing**: AI-determined optimal harvesting periods
- **Market Timing**: Best selling periods based on price predictions
- **Storage Recommendations**: Guidance for post-harvest storage
- **Quality Optimization**: Weather-based quality preservation tips

## 🛠️ Technology Stack

### Backend
- **Flask**: Python web framework
- **scikit-learn**: Machine Learning models
- **Google Generative AI**: AI chatbot and recommendations
- **Pandas & NumPy**: Data processing
- **Requests**: API integrations

### Frontend
- **HTML5 & CSS3**: Modern responsive design
- **JavaScript**: Interactive features and API calls
- **Font Awesome**: Icons and UI elements
- **Chart.js**: Data visualization (ready for implementation)

### APIs Integrated
- **WeatherAPI**: Real-time weather data
- **MarketStack API**: Commodity price data
- **Google Gemini AI**: Advanced AI recommendations

## 📋 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mahack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (Optional - APIs are pre-configured)
   ```bash
   # Create .env file
   touch .env
   
   # Add your API keys (optional - defaults are provided)
   echo "WEATHER_API_KEY=your_weather_api_key" >> .env
   echo "GEMINI_API_KEY=your_gemini_api_key" >> .env
   echo "MARKET_API_KEY=your_market_api_key" >> .env
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the platform**
   Open your browser and navigate to `http://localhost:5000`

## 🎯 Usage Guide

### 1. Dashboard Overview
- **Farming Lifecycle Progress**: Track your farming journey from planning to selling
- **Quick Stats**: Real-time weather, market trends, and risk assessments
- **AI Tools**: Access all AI-powered farming tools from one central location

### 2. AI Crop Doctor
1. Navigate to "AI Crop Doctor" from the dashboard
2. Fill in comprehensive farm information:
   - Location and land size
   - Detailed soil analysis (pH, nutrients)
   - Climate information (rainfall, temperature, humidity)
   - Budget and irrigation setup
3. Get ML-powered crop recommendations with confidence scores
4. Receive AI expert advice and action plans

### 3. Financial AI Advisor
1. Click "Chat with AI" on the Financial AI Advisor card
2. Ask questions about:
   - Loan applications and eligibility
   - Government subsidies and schemes
   - Investment planning and budgeting
   - Financial risk management

### 4. Pest & Disease Monitor
1. Click "Check Crop Health" on the Pest & Disease Monitor card
2. Describe crop symptoms and current conditions
3. Receive AI-powered diagnosis and treatment recommendations

### 5. Harvest Optimizer
1. Click "Plan Harvest" on the Harvest Optimizer card
2. Enter crop type and location
3. Get optimal harvesting timing and market selling strategy

## 🔧 API Endpoints

### Crop Recommendation
```
POST /api/crop-recommendation
Content-Type: application/json

{
  "location": "Delhi",
  "soil_data": {
    "soil_type": "loamy",
    "soil_ph": 6.5,
    "nitrogen": 50,
    "phosphorus": 30,
    "potassium": 40,
    "rainfall": 800,
    "temperature": 28,
    "humidity": 70,
    "land_size": 2
  },
  "budget": 50000
}
```

### Financial Advice
```
POST /api/financial-advice
Content-Type: application/json

{
  "query": "What government schemes are available for wheat farming?",
  "financial_data": {}
}
```

### Pest & Disease Advice
```
POST /api/pest-disease-advice
Content-Type: application/json

{
  "crop": "wheat",
  "symptoms": "Yellow spots on leaves",
  "weather_conditions": "Hot and humid"
}
```

### Price Prediction
```
POST /api/price-prediction
Content-Type: application/json

{
  "crop": "wheat",
  "days_ahead": 30
}
```

## 🌟 Key Innovations

### 1. Hybrid ML + AI Approach
- **Machine Learning**: Accurate crop predictions using Random Forest algorithms
- **AI Enhancement**: Gemini AI provides contextual advice and explanations
- **Combined Intelligence**: Best of both statistical prediction and natural language understanding

### 2. Comprehensive Farming Lifecycle
- **End-to-End Coverage**: From soil analysis to market selling
- **Integrated Workflow**: Seamless transition between different farming stages
- **Contextual Recommendations**: Each suggestion considers the current farming phase

### 3. Real-time Data Integration
- **Live Weather Data**: Up-to-date weather conditions and forecasts
- **Market Price Tracking**: Real-time commodity prices and trends
- **Dynamic Recommendations**: Suggestions that adapt to current conditions

### 4. User-Centric Design
- **Farmer-Friendly Interface**: Simple, intuitive design for all skill levels
- **Local Language Support**: AI responses in Hindi/English mix
- **Mobile-Responsive**: Works on smartphones and tablets

## 📊 Machine Learning Models

### Crop Recommendation Model
- **Algorithm**: Random Forest Classifier
- **Features**: Soil type, pH, nutrients, weather, budget, land size
- **Output**: Top 3 crop recommendations with confidence scores
- **Accuracy**: Trained on agricultural datasets with high prediction accuracy

### Price Forecasting Model
- **Algorithm**: Random Forest Regressor
- **Features**: Historical prices, seasonal patterns, market trends
- **Output**: 30-day price predictions with trend analysis
- **Use Case**: Optimal selling timing recommendations

## 🔮 Future Enhancements

### Planned Features
1. **Drone Integration**: Image-based crop health monitoring
2. **IoT Sensors**: Real-time soil and weather monitoring
3. **Blockchain Marketplace**: Secure, transparent trading platform
4. **Mobile App**: Native iOS and Android applications
5. **Voice Interface**: Hindi/English voice commands for farmers
6. **Community Platform**: Farmer-to-farmer knowledge sharing
7. **Supply Chain Integration**: Direct farm-to-consumer connections

### Advanced AI Features
1. **Computer Vision**: Disease detection from crop images
2. **Predictive Analytics**: Advanced yield forecasting
3. **Climate Adaptation**: Climate change impact analysis
4. **Resource Optimization**: Water and fertilizer usage optimization

## 🤝 Contributing

We welcome contributions to make AgriConnect even better! Here's how you can help:

1. **Bug Reports**: Report issues and bugs
2. **Feature Requests**: Suggest new features
3. **Code Contributions**: Submit pull requests
4. **Documentation**: Improve documentation and guides
5. **Testing**: Help test new features

## 📞 Support & Contact

- **Email**: support@agriconnect.ai
- **GitHub Issues**: For bug reports and feature requests
- **Documentation**: Comprehensive guides available in the repository

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Google Gemini AI** for advanced AI capabilities
- **WeatherAPI** for reliable weather data
- **MarketStack** for commodity price information
- **Open Source Community** for various libraries and tools
- **Agricultural Experts** for domain knowledge and validation

---

**AgriConnect** - Empowering farmers with AI-driven insights for sustainable and profitable agriculture. 🌱🤖📈

