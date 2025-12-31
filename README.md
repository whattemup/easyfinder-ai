"# EasyFinder AI - Enterprise Lead Management System
![EasyFinder AI](https://img.shields.io/badge/EasyFinder-AI-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green)
![React](https://img.shields.io/badge/React-18-blue)

Enterprise-grade AI system for intelligent lead management, scoring, and automated outreach.

## 🎯 Features

- **🤖 Intelligent Lead Scoring**: AI-powered scoring with explainable criteria
- **📊 Interactive Dashboard**: Real-time lead management and analytics
- **📧 Automated Outreach**: NDA-gated email campaigns (mock mode for testing)
- **📝 Audit Trail**: Complete tracking and logging for compliance
- **🔒 Enterprise Security**: Secure implementation with environment-based configuration
- **📤 CSV Import/Export**: Easy lead data management

## 📁 Project Structure

```
EasyFinder AI/
├── backend/
│   ├── easyfinder/          # Core AI modules
│   │   ├── __init__.py
│   │   ├── config.py        # Configuration management
│   │   ├── ingestion.py     # CSV lead ingestion
│   │   ├── scoring.py       # AI lead scoring logic
│   │   ├── outreach.py      # Email outreach (mock/SendGrid)
│   │   ├── logging.py       # Activity logging
│   │   └── main.py          # CLI entry point
│   ├── templates/           # Email templates
│   │   ├── nda_email.html   # NDA email template
│   │   └── demo_email.txt   # Demo email template
│   ├── data/
│   │   ├── leads.csv        # Sample leads data
│   │   └── logs.json        # Activity logs
│   ├── server.py            # FastAPI backend server
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment configuration
├── frontend/
│   ├── src/
│   │   ├── App.js           # Main dashboard component
│   │   └── App.css          # Styles
│   ├── package.json         # Node dependencies
│   └── .env                 # Frontend configuration
└── README.md                # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- MongoDB (local or remote)

### Installation

1. **Clone the repository** (or your files are already in place)

2. **Backend Setup**:
```bash
cd /app/backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables
# Edit .env file with your settings
```

3. **Frontend Setup**:
```bash
cd /app/frontend

# Install Node dependencies
yarn install
```

### Running the Application

#### Option 1: Using Supervisor (Recommended for Production)

```bash
# Start all services
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.out.log
tail -f /var/log/supervisor/frontend.out.log
```

#### Option 2: Manual Start (Development)

**Terminal 1 - Backend**:
```bash
cd /app/backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend**:
```bash
cd /app/frontend
yarn start
```

#### Option 3: CLI Mode (Standalone Python)

```bash
cd /app/backend
python -m easyfinder.main

# Or with custom CSV file
python -m easyfinder.main /path/to/your/leads.csv
```

## 📊 Using the Dashboard

1. **Access the Dashboard**: Open your browser to `http://localhost:3000` (or your configured URL)

2. **Upload Leads**: Click \"Upload CSV\" to import your lead data
   - Required CSV columns: `name`, `email`, `company`, `company_size`, `industry`, `budget`
   - Optional columns: `phone`, `website`

3. **View Leads**: See all leads with their AI-generated scores and priority levels
   - **HIGH Priority** (70-100): Top prospects, automatic email outreach
   - **MEDIUM Priority** (40-69): Good prospects, manual review
   - **LOW Priority** (0-39): Lower priority leads

4. **Process Leads**: Click \"Process Leads\" to:
   - Score all leads using AI criteria
   - Send automated emails to high-priority leads (score >= 70)
   - Log all activities

5. **View Activity Logs**: Switch to \"Activity Logs\" tab to see:
   - Lead scoring events
   - Email sending status
   - CSV upload history

## 🧠 Lead Scoring Logic

The AI scoring system evaluates leads based on multiple criteria:

| Criteria | Points | Description |
|----------|--------|-------------|
| **Company Size** | 10-40 | Enterprise (40), Medium (25), Small (10) |
| **Budget** | 15-30 | >$50k (30), >$25k (15) |
| **Industry** | 10-20 | Target industries (construction, logistics, equipment) get higher scores |
| **Email Validation** | 10 | Valid email format |

**Maximum Score**: 100 points

**Email Threshold**: Leads with score >= 70 receive automated outreach

## 📧 Email Configuration

### Mock Mode (Default - For Testing)

The system runs in **mock mode** by default, which simulates email sending without using a real email service:

```bash
# In backend/.env
SENDGRID_API_KEY=\"mock_key\"
FROM_EMAIL=\"demo@easyfinder.ai\"
APP_ENV=\"local\"
```

Emails are logged to console and activity logs but not actually sent.

### Production Mode (SendGrid)

To enable real email sending:

1. Get a SendGrid API key from [sendgrid.com](https://sendgrid.com)
2. Update `backend/.env`:
```bash
SENDGRID_API_KEY=\"your_actual_sendgrid_api_key\"
FROM_EMAIL=\"your-verified-email@yourdomain.com\"
APP_ENV=\"production\"
```
3. Set `MOCK_EMAIL_MODE = False` in `backend/easyfinder/config.py`
4. Install SendGrid SDK:
```bash
pip install sendgrid
```

## 🔧 Configuration

### Backend Environment Variables

Edit `/app/backend/.env`:

```bash
# Database
MONGO_URL=\"mongodb://localhost:27017\"
DB_NAME=\"test_database\"

# CORS
CORS_ORIGINS=\"*\"

# EasyFinder AI
SENDGRID_API_KEY=\"mock_key\"
FROM_EMAIL=\"demo@easyfinder.ai\"
APP_ENV=\"local\"
```

### Frontend Environment Variables

Edit `/app/frontend/.env`:

```bash
REACT_APP_BACKEND_URL=\"http://localhost:8001\"
```

## 📝 Sample CSV Format

Create a CSV file with the following columns:

```csv
name,email,company,company_size,industry,budget,phone,website
John Smith,john@example.com,TechCorp,enterprise,construction,75000,+1-555-0101,techcorp.com
Sarah Johnson,sarah@example.com,LogisticsPro,medium,logistics,55000,+1-555-0102,logisticspro.com
```

**Required Columns**:
- `name`: Contact name
- `email`: Email address
- `company`: Company name
- `company_size`: enterprise | medium | small
- `industry`: Industry sector
- `budget`: Budget amount (numeric, can include $ and commas)

**Optional Columns**:
- `phone`: Phone number
- `website`: Company website

A sample CSV file is included at `/app/backend/data/leads.csv`

## 🧪 Testing

### Test the Backend API

```bash
# Get all leads
curl http://localhost:8001/api/leads

# Process leads
curl -X POST http://localhost:8001/api/leads/process

# Get activity logs
curl http://localhost:8001/api/logs
```

### Test CLI Mode

```bash
cd /app/backend
python -m easyfinder.main

# Expected output:
# - Lead scoring results
# - Email sending status (mock mode)
# - Processing summary
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/leads` | Get all leads with scores |
| POST | `/api/leads/upload` | Upload CSV file |
| POST | `/api/leads/process` | Process and score leads |
| GET | `/api/logs` | Get activity logs |
| DELETE | `/api/logs` | Clear activity logs |

## 🐳 Deployment

### Docker Deployment (Coming Soon)

### Local Development Deployment

The application is already configured for local development:

1. Backend runs on: `http://localhost:8001`
2. Frontend runs on: `http://localhost:3000`
3. MongoDB runs on: `mongodb://localhost:27017`

### Production Deployment Checklist

- [ ] Update `MONGO_URL` with production database
- [ ] Configure SendGrid with real API key
- [ ] Set `CORS_ORIGINS` to specific domains
- [ ] Enable HTTPS/SSL
- [ ] Set up proper logging and monitoring
- [ ] Configure backup strategy for lead data
- [ ] Review and test email templates
- [ ] Set up rate limiting for API endpoints

## 🔒 Security Notes

- **Mock Mode**: By default, emails are mocked for testing
- **API Keys**: Never commit real API keys to version control
- **CORS**: Configure `CORS_ORIGINS` for specific domains in production
- **Data Privacy**: Ensure compliance with GDPR/privacy regulations
- **NDA**: Update NDA template with your legal requirements

## 🐛 Troubleshooting

### Backend not starting?
```bash
# Check logs
tail -f /var/log/supervisor/backend.err.log

# Verify Python dependencies
cd /app/backend
pip install -r requirements.txt

# Check if port 8001 is in use
lsof -i :8001
```

### Frontend not loading?
```bash
# Check logs
tail -f /var/log/supervisor/frontend.err.log

# Verify Node dependencies
cd /app/frontend
yarn install

# Check backend URL in .env
cat .env | grep REACT_APP_BACKEND_URL
```

### CSV upload failing?
- Ensure CSV has required columns: name, email, company, company_size, industry, budget
- Check file encoding is UTF-8
- Verify file size is reasonable (< 10MB)

### Emails not sending?
- Check if mock mode is enabled (default)
- Verify SendGrid API key if using production mode
- Review email logs in Activity Logs tab

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [SendGrid API Documentation](https://docs.sendgrid.com/)
- [MongoDB Documentation](https://docs.mongodb.com/)

## 🤝 Contributing

This is an enterprise application template. Customize it according to your needs:

1. Update email templates in `/app/backend/templates/`
2. Modify scoring logic in `/app/backend/easyfinder/scoring.py`
3. Customize dashboard UI in `/app/frontend/src/App.js`
4. Add new API endpoints in `/app/backend/server.py`

## 📄 License

Private/Enterprise License - All Rights Reserved

## 🆘 Support

For support and questions:
- Email: demo@easyfinder.ai
- Documentation: This README file
- Logs: Check `/app/backend/data/logs.json`

---

**Built with ❤️ using FastAPI, React, and MongoDB**

**Version**: 1.0.0  
**Last Updated**: 2025
"
