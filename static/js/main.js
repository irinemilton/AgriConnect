// AgriConnect - Smart Farming Dashboard JavaScript
console.log("AgriConnect Smart Farming Dashboard loaded!");

// Global variables
let currentModal = null;
let chatHistory = [];

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
    setupEventListeners();
});

function initializeDashboard() {
    console.log("Initializing smart farming dashboard...");
    showLoadingStates();
}

function showLoadingStates() {
    document.getElementById('current-temp').textContent = 'Loading...';
    document.getElementById('weather-condition').textContent = 'Fetching weather data';
    document.getElementById('market-trend').textContent = 'Loading...';
    document.getElementById('trend-direction').textContent = 'Analyzing market trends';
}

function setupEventListeners() {
    setupModalControls();
    setupChatFunctionality();
    setupFormSubmissions();
}

function setupModalControls() {
    const openChatBtn = document.getElementById('openChat');
    if (openChatBtn) {
        openChatBtn.addEventListener('click', () => openModal('chatModal'));
    }
    
    const checkPestsBtn = document.getElementById('checkPests');
    if (checkPestsBtn) {
        checkPestsBtn.addEventListener('click', () => openModal('pestModal'));
    }
    
    const planHarvestBtn = document.getElementById('planHarvest');
    if (planHarvestBtn) {
        planHarvestBtn.addEventListener('click', () => openModal('harvestModal'));
    }
    
    const closeButtons = document.querySelectorAll('.close');
    closeButtons.forEach(button => {
        button.addEventListener('click', closeModal);
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
        }
    });
}

function setupChatFunctionality() {
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMessage');
    
    if (sendBtn && chatInput) {
        sendBtn.addEventListener('click', sendChatMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
}

function setupFormSubmissions() {
    const pestForm = document.getElementById('pestForm');
    if (pestForm) {
        pestForm.addEventListener('submit', handlePestCheck);
    }
    
    const harvestForm = document.getElementById('harvestForm');
    if (harvestForm) {
        harvestForm.addEventListener('submit', handleHarvestPlanning);
    }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        currentModal = modal;
        document.body.style.overflow = 'hidden';
    }
}

function closeModal() {
    if (currentModal) {
        currentModal.style.display = 'none';
        currentModal = null;
        document.body.style.overflow = 'auto';
    }
}

function sendChatMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    
    if (!chatInput || !chatMessages) return;
    
    const message = chatInput.value.trim();
    if (!message) return;
    
    addChatMessage(message, 'user');
    chatInput.value = '';
    
    fetch('/api/financial-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: message, financial_data: {} })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addChatMessage(data.advice, 'ai');
        } else {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        }
    })
    .catch(error => {
        addChatMessage('Sorry, I\'m having trouble connecting.', 'ai');
        console.error('Chat error:', error);
    });
}

function addChatMessage(message, sender) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}`;
    messageDiv.innerHTML = `<strong>${sender === 'user' ? 'You' : 'AI Advisor'}:</strong> ${message}`;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function handlePestCheck(e) {
    e.preventDefault();
    
    const cropName = document.getElementById('cropName').value;
    const symptoms = document.getElementById('symptoms').value;
    const weatherConditions = document.getElementById('weatherConditions').value;
    const resultsDiv = document.getElementById('pestResults');
    
    if (!cropName || !symptoms) {
        alert('Please fill in the required fields.');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Analyzing crop health...</div>';
    
    fetch('/api/pest-disease-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            crop: cropName,
            symptoms: symptoms,
            weather_conditions: weatherConditions
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resultsDiv.innerHTML = `
                <h4><i class="fas fa-bug"></i> AI Diagnosis & Treatment Plan</h4>
                <div class="ai-response">${data.advice}</div>
                <button class="button" onclick="closeModal()">Close</button>
            `;
        } else {
            resultsDiv.innerHTML = '<div class="error">Sorry, we encountered an error. Please try again.</div>';
        }
    })
    .catch(error => {
        resultsDiv.innerHTML = '<div class="error">Sorry, we\'re having trouble connecting. Please try again later.</div>';
    });
}

function handleHarvestPlanning(e) {
    e.preventDefault();
    
    const crop = document.getElementById('harvestCrop').value;
    const location = document.getElementById('location').value;
    const resultsDiv = document.getElementById('harvestResults');
    
    if (!crop || !location) {
        alert('Please fill in all required fields.');
        return;
    }
    
    resultsDiv.innerHTML = '<div class="loading">Planning your harvest...</div>';
    
    fetch('/api/harvesting-advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ crop: crop, location: location })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            let priceInfo = '';
            if (data.price_prediction) {
                priceInfo = `
                    <div class="price-prediction">
                        <h5>Price Forecast:</h5>
                        <p>Current: ₹${data.price_prediction.current_price}/quintal</p>
                        <p>Predicted (30 days): ₹${data.price_prediction.future_price}/quintal</p>
                        <p>Trend: ${data.price_prediction.trend_percentage}%</p>
                        <p><strong>Recommendation:</strong> ${data.price_prediction.recommendation}</p>
                    </div>
                `;
            }
            
            resultsDiv.innerHTML = `
                <h4><i class="fas fa-cut"></i> Harvest Plan & Market Analysis</h4>
                <div class="ai-response">${data.advice}</div>
                ${priceInfo}
                <button class="button" onclick="closeModal()">Close</button>
            `;
        } else {
            resultsDiv.innerHTML = '<div class="error">Sorry, we encountered an error. Please try again.</div>';
        }
    })
    .catch(error => {
        resultsDiv.innerHTML = '<div class="error">Sorry, we\'re having trouble connecting. Please try again later.</div>';
    });
}

function loadDashboardData() {
    loadWeatherData();
    loadMarketData();
}

function loadWeatherData() {
    fetch('/api/weather?location=Delhi&days=1')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.weather) {
            const weather = data.weather;
            document.getElementById('current-temp').textContent = `${weather.current.temp_c}°C`;
            document.getElementById('weather-condition').textContent = weather.current.condition.text;
        }
    })
    .catch(error => {
        document.getElementById('current-temp').textContent = '28°C';
        document.getElementById('weather-condition').textContent = 'Partly Cloudy';
    });
}

function loadMarketData() {
    fetch('/api/market-prices?crop=wheat')
    .then(response => response.json())
    .then(data => {
        if (data.success && data.market_data && data.market_data.data) {
            const marketData = data.market_data.data[0];
            document.getElementById('market-trend').textContent = `₹${marketData.price}/qtl`;
            const change = marketData.change_percent || 0;
            document.getElementById('trend-direction').textContent = `${change > 0 ? '+' : ''}${change}%`;
        }
    })
    .catch(error => {
        document.getElementById('market-trend').textContent = '₹2,400/qtl';
        document.getElementById('trend-direction').textContent = '+2.5%';
    });
}

// Export functions for global access
window.openModal = openModal;
window.closeModal = closeModal;