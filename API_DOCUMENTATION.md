"# EasyFinder AI - API Documentation

## Base URL
```
Local Development: http://localhost:8001
Production: https://your-domain.com
```

## Authentication
Currently, the API does not require authentication. For production deployment, consider adding API key authentication.

---

## Endpoints

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /api/`

**Response:**
```json
{
  \"message\": \"Hello World\"
}
```

**Example:**
```bash
curl http://localhost:8001/api/
```

---

### 2. Get All Leads

Retrieve all leads with their scores and priority levels.

**Endpoint:** `GET /api/leads`

**Response:**
```json
{
  \"success\": true,
  \"count\": 15,
  \"leads\": [
    {
      \"name\": \"John Smith\",
      \"email\": \"john.smith@techcorp.com\",
      \"company\": \"TechCorp Industries\",
      \"company_size\": \"enterprise\",
      \"industry\": \"construction\",
      \"budget\": \"75000\",
      \"phone\": \"+1-555-0101\",
      \"website\": \"techcorp.com\",
      \"score\": 100,
      \"priority\": \"HIGH\"
    }
    // ... more leads
  ]
}
```

**Query Parameters:**
None

**Example:**
```bash
curl http://localhost:8001/api/leads
```

**Response Codes:**
- `200 OK`: Successfully retrieved leads
- `500 Internal Server Error`: Server error

---

### 3. Upload CSV File

Upload a CSV file containing lead data.

**Endpoint:** `POST /api/leads/upload`

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file with required columns

**Required CSV Columns:**
- `name` - Contact name
- `email` - Email address
- `company` - Company name
- `company_size` - Company size (small, medium, enterprise)
- `industry` - Industry sector
- `budget` - Budget amount

**Optional CSV Columns:**
- `phone` - Phone number
- `website` - Company website

**Response:**
```json
{
  \"success\": true,
  \"message\": \"CSV uploaded successfully\",
  \"filename\": \"leads.csv\"
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/api/leads/upload \
  -F \"file=@/path/to/leads.csv\"
```

**Response Codes:**
- `200 OK`: CSV uploaded successfully
- `400 Bad Request`: Invalid CSV format or missing required columns
- `500 Internal Server Error`: Server error

**CSV Example:**
```csv
name,email,company,company_size,industry,budget,phone,website
John Smith,john@example.com,TechCorp,enterprise,construction,75000,+1-555-0101,techcorp.com
Sarah Johnson,sarah@example.com,LogisticsPro,medium,logistics,55000,+1-555-0102,logisticspro.com
```

---

### 4. Process Leads

Score all leads and send emails to high-priority leads (score >= 70).

**Endpoint:** `POST /api/leads/process`

**Request:**
No body required

**Response:**
```json
{
  \"total_leads\": 15,
  \"high_priority_count\": 10,
  \"emails_sent\": 10,
  \"message\": \"Processed 15 leads successfully\"
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/api/leads/process
```

**Response Codes:**
- `200 OK`: Leads processed successfully
- `500 Internal Server Error`: Server error

**Processing Steps:**
1. Load all leads from database
2. Score each lead using AI algorithm
3. Log scoring events
4. Send NDA emails to leads with score >= 70
5. Log email sending events
6. Return processing summary

---

### 5. Get Activity Logs

Retrieve activity logs for lead scoring and email sending.

**Endpoint:** `GET /api/logs`

**Query Parameters:**
- `limit` (optional): Maximum number of logs to return (default: 100)

**Response:**
```json
{
  \"success\": true,
  \"count\": 50,
  \"logs\": [
    {
      \"timestamp\": \"2025-12-31T06:14:18.947996\",
      \"event\": \"LEAD_SCORED\",
      \"data\": {
        \"name\": \"John Smith\",
        \"email\": \"john.smith@techcorp.com\",
        \"company\": \"TechCorp Industries\",
        \"score\": 100,
        \"priority\": \"HIGH\"
      }
    },
    {
      \"timestamp\": \"2025-12-31T06:14:18.948298\",
      \"event\": \"EMAIL_SENT\",
      \"data\": {
        \"to\": \"john.smith@techcorp.com\",
        \"subject\": \"Private Demo & NDA – EasyFinder AI\",
        \"status\": \"mock_success\",
        \"timestamp\": \"2025-12-31T06:14:18.948294\"
      }
    }
    // ... more logs
  ]
}
```

**Example:**
```bash
# Get last 50 logs
curl http://localhost:8001/api/logs?limit=50

# Get last 100 logs (default)
curl http://localhost:8001/api/logs
```

**Response Codes:**
- `200 OK`: Logs retrieved successfully
- `500 Internal Server Error`: Server error

**Event Types:**
- `LEAD_SCORED`: Lead was scored
- `EMAIL_SENT`: Email was sent to lead
- `CSV_UPLOADED`: CSV file was uploaded
- `EMAIL_FAILED`: Email sending failed

---

### 6. Clear Activity Logs

Delete all activity logs.

**Endpoint:** `DELETE /api/logs`

**Request:**
No body required

**Response:**
```json
{
  \"success\": true,
  \"message\": \"Logs cleared successfully\"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8001/api/logs
```

**Response Codes:**
- `200 OK`: Logs cleared successfully
- `500 Internal Server Error`: Server error

---

## Lead Scoring Algorithm

### Scoring Criteria

The AI scoring system evaluates leads based on multiple criteria:

| Criterion | Points | Description |
|-----------|--------|-------------|
| **Company Size** | | |
| - Enterprise | 40 | Large enterprise company |
| - Medium | 25 | Medium-sized company |
| - Small | 10 | Small business |
| **Budget** | | |
| - > $50,000 | 30 | High budget |
| - > $25,000 | 15 | Medium budget |
| **Industry** | | |
| - Target industries* | 20 | Construction, logistics, equipment |
| - Related industries** | 10 | Manufacturing, transportation, retail |
| **Email Validation** | 10 | Valid email format |

*Target industries: construction, logistics, equipment  
**Related industries: manufacturing, transportation, retail

### Priority Levels

Based on the calculated score:

- **HIGH Priority** (70-100): Automatic email outreach
- **MEDIUM Priority** (40-69): Manual review recommended
- **LOW Priority** (0-39): Lower priority follow-up

### Score Calculation Example

```python
# Example lead
lead = {
    \"company_size\": \"enterprise\",  # +40 points
    \"budget\": \"75000\",             # +30 points (>$50k)
    \"industry\": \"construction\",    # +20 points (target)
    \"email\": \"john@example.com\"    # +10 points (valid)
}
# Total score: 100 points
# Priority: HIGH
# Action: Send email automatically
```

---

## Email Templates

### NDA Email Template

High-priority leads (score >= 70) receive an automated NDA and demo invitation email.

**Subject:** Private Demo & NDA – EasyFinder AI

**Template Location:** `/app/backend/templates/nda_email.html`

**Placeholders:**
- `{{name}}` - Lead's name
- `{{company}}` - Company name

---

## Error Responses

All error responses follow this format:

```json
{
  \"detail\": \"Error message description\"
}
```

**Common Error Codes:**
- `400 Bad Request`: Invalid input data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, no rate limiting is implemented. For production deployment, consider adding rate limiting to prevent abuse.

**Recommended Limits:**
- `/api/leads`: 100 requests/minute
- `/api/leads/upload`: 10 requests/minute
- `/api/leads/process`: 5 requests/minute
- `/api/logs`: 50 requests/minute

---

## WebSocket Support

WebSocket support is not currently implemented. Consider adding for real-time updates in future versions.

---

## Examples

### Python Example

```python
import requests

# Base URL
BASE_URL = \"http://localhost:8001/api\"

# Get all leads
response = requests.get(f\"{BASE_URL}/leads\")
leads = response.json()
print(f\"Found {leads['count']} leads\")

# Upload CSV
with open('leads.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post(f\"{BASE_URL}/leads/upload\", files=files)
    print(response.json())

# Process leads
response = requests.post(f\"{BASE_URL}/leads/process\")
result = response.json()
print(f\"Processed {result['total_leads']} leads\")
print(f\"High priority: {result['high_priority_count']}\")
print(f\"Emails sent: {result['emails_sent']}\")

# Get logs
response = requests.get(f\"{BASE_URL}/logs?limit=10\")
logs = response.json()
for log in logs['logs']:
    print(f\"{log['timestamp']}: {log['event']}\")
```

### JavaScript Example

```javascript
const BASE_URL = 'http://localhost:8001/api';

// Get all leads
async function getLeads() {
  const response = await fetch(`${BASE_URL}/leads`);
  const data = await response.json();
  console.log(`Found ${data.count} leads`);
  return data.leads;
}

// Upload CSV
async function uploadCSV(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${BASE_URL}/leads/upload`, {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Process leads
async function processLeads() {
  const response = await fetch(`${BASE_URL}/leads/process`, {
    method: 'POST'
  });
  
  const data = await response.json();
  console.log(`Processed ${data.total_leads} leads`);
  console.log(`High priority: ${data.high_priority_count}`);
  console.log(`Emails sent: ${data.emails_sent}`);
  
  return data;
}

// Get logs
async function getLogs(limit = 50) {
  const response = await fetch(`${BASE_URL}/logs?limit=${limit}`);
  const data = await response.json();
  
  data.logs.forEach(log => {
    console.log(`${log.timestamp}: ${log.event}`);
  });
  
  return data.logs;
}
```

### cURL Examples

```bash
# Get all leads
curl http://localhost:8001/api/leads

# Upload CSV
curl -X POST http://localhost:8001/api/leads/upload \
  -F \"file=@leads.csv\"

# Process leads
curl -X POST http://localhost:8001/api/leads/process

# Get logs (last 50)
curl \"http://localhost:8001/api/logs?limit=50\"

# Clear logs
curl -X DELETE http://localhost:8001/api/logs

# Pretty print JSON
curl http://localhost:8001/api/leads | python -m json.tool
```

---

## API Versioning

Current version: `v1` (implicit, no version in URL)

For future versions, consider adding version to URL:
- `/api/v1/leads`
- `/api/v2/leads`

---

## CORS Configuration

CORS is configured to allow all origins by default (`*`). For production, update to specific domains:

```python
# In backend/.env
CORS_ORIGINS=\"https://yourdomain.com,https://www.yourdomain.com\"
```

---

## Future API Enhancements

Planned features for future versions:

1. **Authentication & Authorization**
   - API key authentication
   - JWT tokens
   - Role-based access control

2. **Advanced Filtering**
   - Filter leads by score range
   - Filter by priority level
   - Filter by industry
   - Search by company name

3. **Batch Operations**
   - Bulk update leads
   - Bulk delete leads
   - Export filtered leads

4. **Analytics Endpoints**
   - Lead score distribution
   - Industry breakdown
   - Email campaign performance
   - Conversion tracking

5. **WebSocket Support**
   - Real-time lead updates
   - Live processing status
   - Instant notifications

---

## Support

For API questions and issues:
- Email: demo@easyfinder.ai
- Documentation: `/app/README.md`
- GitHub Issues: [Repository URL]

---

**API Version:** 1.0.0  
**Last Updated:** 2025
"
