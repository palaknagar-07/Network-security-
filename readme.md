# Network Security ML Project

A comprehensive machine learning pipeline for phishing website detection using MongoDB Atlas data storage and advanced data validation.

## 🎯 Project Overview

This project implements a complete ML pipeline for detecting phishing websites using network security features. The system includes:

- **Data Ingestion**: Automated data extraction from MongoDB Atlas
- **Data Validation**: Schema validation and drift detection
- **Feature Engineering**: Preprocessing for ML models
- **Model Training**: Multiple algorithm comparison
- **Evaluation**: Comprehensive model assessment

## 📊 Dataset

**Source**: Phishing detection dataset with 11,055 records
**Features**: 31 network security features including:
- IP Address validation
- URL characteristics
- SSL certificate analysis
- Domain registration details
- Web traffic patterns
- Page ranking metrics

**Target Variable**: `Result` (-1: Legitimate, 1: Phishing)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Virtual environment

### Installation

```bash
# Clone repository
git clone <repository-url>
cd "Network Security (ML)"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

1. Create `.env` file with MongoDB credentials:
```env
MONGODB_URL=mongodb+srv://your_username:your_password@your_server
```

2. Install the project:
```bash
pip install -e .
```

## 🏃‍♂️ Running the Pipeline

### Complete Pipeline
```bash
python main.py
```

This executes:
1. **Data Ingestion**: Extracts data from MongoDB Atlas
2. **Data Validation**: Validates schema and checks for drift
3. **Feature Engineering**: Processes features for ML
4. **Model Training**: Trains and evaluates models

### Individual Components

#### Data Ingestion Only
```python
from NetworkSecurity.components.data_ingestion import DataIngestion
from NetworkSecurity.entity.config_entity import DataIngestionConfig, TrainingPipelineConfig

training_pipeline_config = TrainingPipelineConfig()
data_ingestion_config = DataIngestionConfig(training_pipeline_config)
data_ingestion = DataIngestion(data_ingestion_config)
artifact = data_ingestion.initiate_data_ingestion()
```

#### Data Validation Only
```python
from NetworkSecurity.components.data_validation import DataValidation
from NetworkSecurity.entity.config_entity import DataValidationConfig

data_validation_config = DataValidationConfig(training_pipeline_config)
data_validation = DataValidation(data_ingestion_artifact, data_validation_config)
validation_artifact = data_validation.initiate_data_validation()
```

## 📁 Project Structure

```
Network Security (ML)/
├── main.py                     # Main pipeline execution
├── requirements.txt              # Dependencies
├── setup.py                    # Package configuration
├── .env                        # Environment variables
├── NetworkSecurity/             # Main package
│   ├── components/              # Pipeline components
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   └── data_transformation.py
│   ├── entity/                  # Data classes
│   │   ├── config_entity.py
│   │   └── artifact_entity.py
│   ├── constant/                # Configuration constants
│   │   └── training_pipeline/
│   ├── utils/                   # Utility functions
│   │   └── main_utils.py/
│   ├── exception/               # Custom exceptions
│   └── logging/                 # Logging configuration
├── data_schema/                # Data validation schema
│   └── schema.yaml
├── Network_Data/               # Raw data files
└── artifacts/                  # Generated artifacts
    └── [timestamp]/
        ├── data_ingestion/
        ├── data_validation/
        └── data_transformation/
```

## 🔧 Configuration

### Schema Configuration (`data_schema/schema.yaml`)

```yaml
columns:
  - having_IP_Address: int64
  - URL_Length: int64
  - Shortining_Service: int64
  # ... (31 total columns)
  - Result: int64

numerical_columns:
  - having_IP_Address
  - URL_Length
  # ... (all numeric columns)
  - Result
```

### Pipeline Constants

- **Database**: `NetworkSecurity`
- **Collection**: `PhishingData`
- **Train/Test Split**: 80/20
- **Drift Threshold**: 0.05 (p-value)

## 📈 Artifacts Generated

### Data Ingestion Artifacts
```
artifacts/[timestamp]/data_ingestion/
├── feature_store/
│   └── phisingData.csv           # Complete dataset
└── ingested/
    ├── train.csv                 # Training split (80%)
    └── test.csv                  # Test split (20%)
```

### Data Validation Artifacts
```
artifacts/[timestamp]/data_validation/
├── drift_report/
│   └── report.yaml               # Drift analysis results
├── valid_train.csv              # Validated training data
└── valid_test.csv               # Validated test data
```

## 🔍 Data Validation Features

### Schema Validation
- **Column Count**: Verifies expected number of columns (31)
- **Column Names**: Matches schema exactly
- **Data Types**: Validates all columns are numeric

### Drift Detection
- **Statistical Test**: Kolmogorov-Smirnov (KS) test
- **Threshold**: p-value < 0.05 indicates drift
- **Report**: Detailed p-values and drift status per column

### Validation Status
```python
DataValidationArtifact(
    validation_status=True,           # Overall validation result
    valid_train_file_path=...,       # Validated training data
    valid_test_file_path=...,        # Validated test data
    drift_report_file_path=...        # Drift analysis report
)
```

## 🐛 Troubleshooting

### Common Issues

#### MongoDB Connection Issues
```bash
# Check environment variables
python -c "import os; print(os.getenv('MONGODB_URL'))"

# Test connection manually
python -c "from pymongo import MongoClient; print(MongoClient(os.getenv('MONGODB_URL')).list_database_names())"
```

#### Validation Failures
```bash
# Check schema match
python -c "
import pandas as pd
from NetworkSecurity.utils.main_utils.utils import read_yaml_file
schema = read_yaml_file('data_schema/schema.yaml')
df = pd.read_csv('artifacts/latest/data_ingestion/ingested/train.csv')
print(f'Schema columns: {len(schema[\"columns\"])}')
print(f'Dataframe columns: {len(df.columns)}')
"
```

#### Module Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall package
pip install -e .
```

## 📊 Model Performance

### Expected Metrics
- **Accuracy**: > 90%
- **Precision**: > 85%
- **Recall**: > 85%
- **F1-Score**: > 85%

### Feature Importance
Top features typically include:
- SSL certificate validity
- URL length and characteristics
- Domain registration details
- Web traffic patterns

## 🤝 Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Make changes and test: `python main.py`
4. Submit pull request

## 📄 License

This project is licensed under the MIT License.

## 🔄 GitHub Actions Troubleshooting

### Quick Fixes

**MongoDB Error**: Add `MONGODB_URL` to repository secrets (Settings → Secrets)

**Deprecated Actions**: Update workflow to use `@v4` versions

**Permission Issues**: Add workflow permissions in YAML

**Python Errors**: Check `requirements.txt` and run `pip install -e .`

### Setup Required
- Add `MONGODB_URL` secret to GitHub repository
- Test locally: `python main.py`
- Check workflow logs in Actions tab

## �� Support

For questions or issues:
- Check logs in `logs/` directory
- Verify MongoDB Atlas connection
- Validate schema configuration
- Ensure all dependencies are installed
- Review GitHub Actions workflow logs
- Check repository secrets configuration

---

**Note**: This pipeline is designed for production use with comprehensive logging, error handling, and data validation to ensure reliable ML model training and deployment.