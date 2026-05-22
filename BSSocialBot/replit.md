# UMD Combined BS/MS Program Eligibility Tool

## Overview

This is a Flask-based web application that serves as an interactive eligibility assessment tool for the University of Maryland's Combined BS/MS Program in Computer Science. The application features a conversational chatbot interface that guides students through a step-by-step assessment process to determine their eligibility for the program. The bot collects student information such as academic performance, semester codes, and other requirements through a structured conversation flow.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Static Web Interface**: Built with HTML templates using Jinja2 templating engine
- **UI Framework**: Bootstrap with dark theme for responsive design
- **Interactive Elements**: Vanilla JavaScript for chat functionality with real-time messaging
- **Styling**: Custom CSS with Font Awesome icons for enhanced user experience

### Backend Architecture
- **Web Framework**: Flask application with session-based state management
- **Conversation Engine**: Custom chatbot logic in `bsms_bot.py` that handles multi-step conversations
- **Session Management**: Flask sessions store conversation state and user responses across interactions
- **Route Structure**: RESTful endpoints for chat interactions, session reset, and health checks

### State Management
- **Session Storage**: User conversation data persists in Flask sessions with step tracking
- **Conversation Flow**: Step-based progression through eligibility questions with response validation
- **Data Structure**: Nested dictionary storing current step and accumulated user responses

### Business Logic
- **Semester Code Processing**: Robust semester code normalization and validation (FA/SP format)
- **Date Calculations**: Semester start date computation and semester interval calculations
- **Academic Timeline**: Functions for calculating previous semesters and academic progression

## External Dependencies

### Core Framework Dependencies
- **Flask**: Web application framework for routing, templating, and session management
- **Python Standard Library**: datetime and re modules for date processing and regex validation

### Frontend Dependencies
- **Bootstrap**: CSS framework loaded via CDN for responsive UI components
- **Font Awesome**: Icon library via CDN for visual enhancements
- **Custom Bootstrap Theme**: Replit's dark theme variant for consistent styling

### Development and Deployment
- **Environment Variables**: SESSION_SECRET for production security configuration
- **Health Check Endpoint**: `/health` route for deployment monitoring and load balancer integration
- **Development Server**: Built-in Flask development server with debug mode support