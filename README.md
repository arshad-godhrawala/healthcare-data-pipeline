# Healthcare Data Pipeline

A comprehensive healthcare data processing pipeline designed to ingest, process, and analyze patient data with real-time monitoring capabilities. This system provides RESTful APIs, time-series forecasting, and a web-based dashboard for healthcare data management.

## 🏥 Overview

This healthcare pipeline processes patient information, vital signs, and medical history data to provide real-time insights and predictive analytics for healthcare providers. The system ensures data security and follows healthcare data handling best practices.

## 🏗️ Architecture

```
[Patient Data] → [Data Ingestion] → [Processing Pipeline] → [Database Storage] → [API Services] → [Dashboard]
```

## 🔧 Components

### **Database Layer**
- **PostgreSQL** - Primary relational database for patient data, vital signs, and medical history
- **InfluxDB** - Time-series database for real-time vital signs monitoring
- **Docker Compose** - Database orchestration and management

### **Data Ingestion & Processing**
- **Patient Data Loader** - Loads and manages patient information
- **Sensor Data Collector** - Collects real-time vital signs data
- **Data Aggregator** - Statistical analysis and data summarization
- **Feature Engineer** - Creates health metrics and risk indicators

### **Analytics & Forecasting**
- **Health Forecaster** - Time-series forecasting for health trends
- **Prophet** - Facebook's forecasting library for time-series analysis
- **Statsmodels** - Statistical modeling and analysis
- **Pandas & NumPy** - Data manipulation and numerical computing

### **API Services**
- **FastAPI** - High-performance REST API framework
- **Uvicorn** - ASGI server for API deployment
- **Pydantic** - Data validation and serialization
- **SQLAlchemy** - Database ORM and connection management

### **Frontend Dashboard**
- **HTML/CSS/JavaScript** - Web-based dashboard interface
- **HTTP Server** - Simple dashboard server with CORS support
- **Real-time Data Visualization** - Patient monitoring interface

### **Monitoring & Testing**
- **System Health Checks** - Automated system monitoring
- **API Testing Suite** - Comprehensive endpoint testing
- **Database Connectivity Tests** - Connection validation

## 📋 Prerequisites

- **Python 3.9+**
- **Docker & Docker Compose**
- **Git**
- **8GB+ RAM** (recommended)
- **5GB+ free disk space**

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/arshad-godhrawala/healthcare-data-pipeline.git
cd healthcare-data-pipeline
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
# PostgreSQL Configuration
POSTGRES_USER=healthcare_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=healthcare_db

# InfluxDB Configuration
INFLUXDB_USER=admin
INFLUXDB_PASSWORD=your_secure_password
INFLUXDB_ORG=healthcare_org
INFLUXDB_BUCKET=vital_signs
INFLUXDB_TOKEN=your_influxdb_token
```

### 4. Start Database Services
```bash
docker-compose up -d postgres influxdb
```

## ⚡ Quick Start

### Method 1: Automated System Check
```bash
python check_system.py
```

### Method 2: Manual Setup

1. **Start the API Server**
```bash
python run_api.py
```

2. **Start the Dashboard**
```bash
python simple_dashboard.py
```

3. **Verify System Status**
```bash
python test_system.py
```

## 🔗 Access Points

Once the system is running, you can access:

- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Interactive API**: http://localhost:8000/redoc
- **Dashboard**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Patient Management
- `GET /patients` - Retrieve all patients
- `GET /patients/{patient_id}` - Get specific patient
- `POST /patients` - Add new patient
- `PUT /patients/{patient_id}` - Update patient information

### Vital Signs
- `GET /vitals/{patient_id}` - Get patient vital signs
- `POST /vitals` - Add new vital sign record
- `GET /vitals/{patient_id}/latest` - Get latest vital signs

### Health Monitoring
- `GET /health-monitoring` - System health dashboard data
- `GET /forecast/{patient_id}` - Health trend forecasting
- `GET /patients/{patient_id}/summary` - Patient health summary

### System
- `GET /health` - API health status
- `GET /` - Welcome message

## 💾 Data Models

### Patient
```python
{
    "patient_id": int,
    "patient_name": str,
    "age": int,
    "gender": str,
    "contact_info": str
}
```

### Vital Signs
```python
{
    "vital_id": int,
    "patient_id": int,
    "timestamp": datetime,
    "heart_rate": float,
    "blood_pressure": str,
    "temperature": float,
    "oxygen_saturation": float
}
```

### Medical History
```python
{
    "history_id": int,
    "patient_id": int,
    "diagnosis": str,
    "treatment": str,
    "date_diagnosed": date
}
```

## 🧪 Testing

### Run All Tests
```bash
python test_system.py
```

### Individual Component Tests
```bash
# Test database connections
python test_db_query.py

# Test API functionality
python test_api_function.py

# Test dashboard
python test_dashboard_simple.py
```

## 🛠️ Troubleshooting

### Dashboard Not Starting
```bash
# Method 1: Manual dashboard start
python simple_dashboard.py

# Method 2: Direct HTTP server
cd frontend
python -m http.server 3000

# Method 3: Alternative port
cd frontend
python -m http.server 8080
```

### API Connection Issues
```bash
# Check if API is running
curl http://localhost:8000/health

# Restart API server
python run_api.py
```

### Database Connection Problems
```bash
# Restart database services
docker-compose down
docker-compose up -d

# Check database status
docker-compose ps
```

### Port Conflicts
If you encounter port conflicts:
- **API Server**: Modify port in `run_api.py`
- **Dashboard**: Try alternative ports (3001, 8080, 8001)
- **Databases**: Check `docker-compose.yml` for port mappings

## 📈 Features

- ✅ **Real-time Vital Signs Monitoring**
- ✅ **Patient Data Management**
- ✅ **Health Trend Forecasting**
- ✅ **RESTful API with Interactive Documentation**
- ✅ **Web Dashboard Interface**
- ✅ **Time-series Data Storage**
- ✅ **Statistical Health Analytics**
- ✅ **Automated System Health Checks**
- ✅ **CORS-enabled Frontend**
- ✅ **Comprehensive Testing Suite**

## 🗂️ Project Structure

```
healthcare-pipeline/
├── src/
│   ├── api/                 # FastAPI application
│   ├── database/            # Database models and operations
│   ├── data_ingestion/      # Data loading and collection
│   ├── data_processing/     # Data analysis and aggregation
│   └── forecasting/         # Health prediction models
├── frontend/                # Web dashboard files
├── scripts/                 # Utility scripts
├── docker-compose.yml       # Database services
├── requirements.txt         # Python dependencies
├── run_api.py              # API server launcher
├── simple_dashboard.py     # Dashboard server
└── check_system.py         # System health check
```

## 🔒 Security & Compliance

- **Data Encryption**: All sensitive data is properly secured
- **Input Validation**: Pydantic models ensure data integrity
- **CORS Configuration**: Secure cross-origin resource sharing
- **Database Security**: Containerized database with proper authentication
- **API Security**: Request validation and error handling

## 📦 Dependencies

**Core Libraries:**
- `pandas==2.1.0` - Data manipulation
- `numpy==1.24.3` - Numerical computing
- `fastapi==0.103.1` - Web framework
- `uvicorn==0.23.2` - ASGI server
- `sqlalchemy==2.0.20` - Database ORM
- `psycopg2-binary==2.9.7` - PostgreSQL adapter
- `influxdb-client==1.38.0` - InfluxDB client
- `pydantic==2.3.0` - Data validation

**Analytics & Visualization:**
- `matplotlib==3.7.2` - Plotting library
- `seaborn==0.12.2` - Statistical visualization
- `plotly==5.15.0` - Interactive plots
- `prophet==1.1.4` - Time-series forecasting
- `statsmodels==0.14.0` - Statistical analysis

<!-- **Development & Testing:**
- `pytest==7.4.0` - Testing framework
- `requests==2.31.0` - HTTP library
- `jinja2==3.1.2` - Template engine -->

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For issues and questions:
1. Check the troubleshooting section above
2. Run `python check_system.py` for system diagnostics
3. Review the API documentation at http://localhost:8000/docs
4. Open an issue on GitHub

---

**🎉 Your Healthcare Data Pipeline is ready for deployment!**

### Quick Verification:
1. Run `python check_system.py`
2. Visit http://localhost:8000/docs
3. Start dashboard with `python simple_dashboard.py`

**Built with ❤️ for healthcare data management**