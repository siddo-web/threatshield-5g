# ThreatShield 5G

AI-driven threat detection and mitigation platform for 5G/6G networks.

## Stage 1: Backend Foundation (Verified)

### Quick Start

```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run tests
pytest -q

# Generate synthetic data and train models
python -m backend.scripts.seed
```

### Project Structure

```
backend/
├── app/                    # FastAPI application
│   ├── config.py          # Settings and configuration
│   ├── database.py        # SQLAlchemy database setup
│   ├── main.py            # FastAPI app instance
│   ├── models/            # Pydantic and ORM models
│   └── services/          # Business logic services
├── ml/                    # Machine learning modules
│   ├── preprocessing.py   # Data pipeline
│   ├── synthetic_data.py  # Traffic generation
│   ├── detector.py        # Random Forest detector
│   ├── zero_day.py        # Autoencoder anomaly detection
│   ├── metrics.py         # Evaluation metrics
│   └── model_registry.py  # Model loading/saving
├── scripts/
│   └── seed.py            # Demo data initialization
├── tests/                 # Pytest test suite
└── requirements.txt       # Dependencies

data/sample/              # Sample datasets
models/                   # Trained model artifacts
```

### Stage 1 Artifacts

- ✅ Data preprocessing pipeline (normalization, imputation, encoding, scaling, SMOTE)
- ✅ Synthetic network traffic generator (6 threat classes + Benign)
- ✅ Random Forest detector (200 trees, balanced class weights)
- ✅ Autoencoder anomaly detection (PyTorch, reconstruction error scoring)
- ✅ Metrics computation (accuracy, precision, recall, F1, FPR)
- ✅ Database models (SQLAlchemy ORM)
- ✅ Comprehensive test suite (8 test modules, 15+ test cases)
- ✅ Demo seed script (generates 1500 samples, trains detector, creates alerts)

### Tests Included

```bash
pytest backend/tests/test_metrics.py          # Metric calculation tests
pytest backend/tests/test_preprocessing.py    # Data pipeline tests
pytest backend/tests/test_prediction.py       # Detector inference tests
pytest backend/tests/test_mitigation.py       # Mitigation mapping tests
pytest backend/tests/test_anomaly.py          # Autoencoder tests
pytest backend/tests/test_api.py              # FastAPI endpoint tests
pytest backend/tests/test_synthetic_generator.py  # Traffic generation tests
```

### Running Stage 1 Validation

```bash
# Install
pip install -r backend/requirements.txt

# Run all tests
pytest -q

# Generate demo data and train models
python -m backend.scripts.seed
# Output:
# {
#   "rows": 1500,
#   "metrics": {
#     "model": "RandomForest",
#     "accuracy": 0.XX,
#     "precision": 0.XX,
#     "recall": 0.XX,
#     "f1": 0.XX,
#     "false_positive_rate": 0.XX,
#     "confusion_matrix": [...],
#     "inference_latency_ms": 0.0
#   }
# }
```

### Output Artifacts After Seed

- `data/sample/5g_nidd_sample.csv` - Synthetic traffic dataset (1500 samples)
- `models/detector/random_forest.joblib` - Trained detector model
- `models/detector/preprocessor.joblib` - Feature preprocessor
- `models/detector/label_encoder.joblib` - Label encoder mapping
- `models/zero_day/autoencoder.pt` - Trained autoencoder
- `models/metrics/random_forest.json` - Training metrics
- `threatshield.db` - SQLite database with demo users and alerts

### Next: Stage 2

- FastAPI prediction endpoints
- JWT authentication
- Alert management API
- Real-time threat scoring
- Mitigation action recommendations

---

**Status:** ✅ Stage 1 Complete and Verified
