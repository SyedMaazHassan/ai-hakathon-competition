# 🚨 Frontline Worker Support AI - Emergency Response Pipeline

**AI-powered emergency response system for Pakistan's frontline workers**
*Built for AI Hackathon Competition*

## 🎯 Overview

An intelligent emergency response system that connects citizens with the right government departments instantly. Using multi-agent AI orchestration, it processes emergency requests, determines criticality, and triggers appropriate actions via SMS, email, and voice calls.

## ⚡ Quick Start

```bash
# 1. Clone & Setup
git clone <repository-url>
cd ai-hakathon-competition

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Environment Setup
cp .env.example .env
# Add your API keys: Google Maps, Gemini, ZeptoMail, Twilio

# 4. Database Setup
python manage.py migrate

# 5. Run the System
python manage.py runserver
```

## 🤖 AI Agents Architecture

**Multi-Agent Emergency Processing Pipeline:**

1. **Router Agent** - Classifies emergency type and department
2. **Matcher Service** - Finds closest government entity using Google Maps
3. **Department Agent** - Creates action plans with criticality assessment
4. **Trigger Orchestrator** - Orchestrates multi-channel communications
5. **Action Executor** - Executes SMS, email, and VAPI voice calls
6. **Next Steps Agent** - Provides citizen guidance

## 🚨 Emergency Response Flow

```
Citizen Request → Router → Matcher → Department Agent → Trigger Actions
                                         ↓
Critical: Voice Call + SMS + Email (Immediate)
High: Voice Call + SMS + Email (Urgent)
Medium: Email + SMS (Normal)
Low: Email (Standard)
```

## 🔧 Key Features

- **Intelligent Triage** - AI determines emergency criticality
- **Multi-Channel Alerts** - SMS, Email, Voice calls via VAPI
- **Location-Aware** - Google Maps integration for precise routing
- **Personalized Communications** - User names in all messages
- **Database Persistence** - Complete audit trail
- **Degraded Mode** - Works without internet/AI for critical situations

## 📱 Communication Examples

**Critical Emergency SMS:**
```
🚨 Hello Ahmad, EMERGENCY LOGGED: Lahore Fire Department has been contacted immediately. Stay safe. Help is on the way. Ref: 12AB34CD
```

**Action Plan Email:**
```
🚨 CRITICAL EMERGENCY - Action Plan for Your Request

Your emergency: House fire with trapped residents
Location: Model Town, Lahore

IMMEDIATE ACTIONS:
1. Fire trucks dispatched - 5 minutes
2. Paramedics en route - 8 minutes

FOLLOW-UP ACTIONS:
1. Investigation team - 2 hours
2. Damage assessment - 24 hours

Reference: 12AB34CD
```

## 🗄️ Project Structure

```
apps/
├── depts/
│   ├── agents/           # AI Agents (Router, Department, NextSteps)
│   ├── services/         # Core Services (Pipeline, Matcher, Actions)
│   └── models.py         # Database models
├── authentication/       # User management
└── core/                 # Base functionality

Key Files:
├── simplified_emergency_pipeline.py  # Main orchestrator
├── trigger_orchestrator_service.py   # Action coordination
├── action_executor.py                # Multi-channel execution
└── test_*.py                         # Comprehensive testing
```

## 🧪 Testing

```bash
# Test individual components
python test_router_agent.py
python test_matcher_service.py
python test_sms_action_service.py

# Test complete pipeline
python test_simplified_pipeline.py
```

## 📊 Database Models

- **CitizenRequest** - Emergency request tracking
- **ActionLog** - All triggered actions audit
- **NotificationLog** - SMS/Email delivery tracking
- **EmergencyCall** - VAPI voice call records

## 🔑 Environment Variables

```env
# AI Services
GOOGLE_MAPS_API_KEY=your_google_maps_key
GEMINI_API_KEY=your_gemini_key

# Communication
ZEPTOMAIL_API_KEY=your_zeptomail_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# Database
DB_NAME=emergency_db
DB_USER=postgres
DB_PASSWORD=your_password
```

## 🎖️ Competition Features

**Judge Wow Factors:**
- ✅ Real VAPI voice calls to departments
- ✅ Intelligent criticality assessment
- ✅ Multi-channel orchestrated responses
- ✅ Google Maps location integration
- ✅ Personalized communications
- ✅ Complete audit trail
- ✅ Degraded mode fallbacks

## 🚀 Demo Scenarios

1. **Critical Fire Emergency** - Voice calls + immediate SMS/email
2. **Traffic Accident** - SMS alerts + action plan emails
3. **Noise Complaint** - Standard email processing
4. **Medical Emergency** - Full multi-channel response

## 📞 Contact

Built for AI Hackathon Competition
Team: Frontline Worker Support AI

---

**🎯 Mission:** Connecting Pakistan's citizens with emergency services through intelligent AI orchestration.