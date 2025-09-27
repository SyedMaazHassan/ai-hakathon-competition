# Multi-Agent System for Citizen Request Processing

## System Overview
A streamlined multi-agent architecture that processes citizen requests, routes them to appropriate government departments, and takes automated actions based on urgency levels.

---

## Agent Definitions

### 1. **Router Agent**
**Role:** Request Classification  
**Input:** Raw citizen request text  
**Output:** Department category (Police, Fire, Health, etc.)  
**Implementation:** LLM-based classification with keyword fallback for reliability  

### 2. **Department Agent (Orchestrator)**
**Role:** Workflow coordination and decision making  
**Input:** Categorized request + user location  
**Output:** Complete action plan execution  
**Responsibilities:**
- Assess urgency level (Low/Medium/High/Critical)
- Coordinate with Matcher Service for entity selection
- Create comprehensive action plan
- Execute actions via service calls
- Generate user response
- Schedule follow-ups

### 3. **Next-Steps Agent**
**Role:** User communication  
**Input:** Action plan and execution results  
**Output:** Clear explanation in Urdu/English of what happened and next steps  
**Purpose:** Translate technical actions into user-friendly guidance

### 4. **Follow-Up Agent**
**Role:** Automated monitoring and persistence  
**Input:** Request with expected response timeline  
**Output:** Status checks and escalation if needed  
**Behavior:** Scheduled watchdog with bounded retries (max 3 attempts with exponential backoff)

---

## Supporting Services (Non-Agents)

### **Matcher Service**
Finds the best department entity (hospital, police station, office) based on:
- Request category
- User location (same city priority)
- Entity availability and capacity

### **Execution Services**
Infrastructure components that handle:
- **Voice Calls:** VAPI integration for emergency calls
- **Email/SMS:** Notifications to departments and users
- **Calendar:** Google Calendar appointment booking
- **Database:** Request status and action logging

---

## Workflow Flow
```
User Request → Router Agent → Department Agent (Orchestrator)
                                    ↓
            Next-Steps Agent ← Department Agent → Follow-Up Agent
```

## Key Features
- **Degradation Mode:** AI failures trigger rule-based fallbacks
- **Multi-language:** Support for Urdu and English
- **Emergency Priority:** Critical cases get immediate voice calls
- **Bounded Retries:** Prevents infinite loops in follow-ups
- **Location-Aware:** Routes to same-city department entities

This architecture ensures reliable request processing while maintaining simplicity for rapid development and easy debugging.