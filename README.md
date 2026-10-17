# KisanSetu 🌱

**AI-powered agricultural assistance for farmers**

KisanSetu is a hackathon project designed to help farmers access agricultural insights through machine learning, crop disease identification, and market-price information.

> **Project status:** Initial setup and development. ML training, evaluation, and deployment are pending implementation and verification.

## 🎯 Project Goals

- Identify plant diseases from leaf images.
- Provide disease predictions with confidence scores.
- Support tomato and potato disease detection in the initial demo.
- Prepare model inference for integration with the application.
- Process mandi price data for agricultural price insights.
- Evaluate model performance on unseen images before deployment.

## 🧠 Machine Learning Module

The ML module is developed inside `workspace-ml/`.

### Planned Technology Stack

- **Python:** 3.13
- **PyTorch and torchvision:** Model training and image processing
- **timm:** Pretrained image classification architectures
- **scikit-learn:** Model evaluation
- **Pillow and NumPy:** Image processing and numerical operations
- **ONNX and ONNX Runtime:** Model export and inference

### Planned Model Pipeline

1. Download and inspect labelled plant disease datasets.
2. Prepare image preprocessing and augmentation.
3. Fine-tune a pretrained EfficientNet-B0 classifier.
4. Evaluate using top-1 accuracy, macro-F1, and a confusion matrix.
5. Test performance on field-style images.
6. Calibrate prediction confidence using validation data.
7. Export the trained model to ONNX.
8. Integrate the inference module with the application.

The architecture and pipeline are planned choices. Final model performance will be reported only after actual evaluation.

## 📂 Project Structure

```text
HACKSHIFT-IITD-SNACKOVERFLOW/
│
├── contracts/                 # Shared interfaces and contracts
├── deploy/                    # Application deployment
├── docs/                      # Project documentation
├── infra/                     # Infrastructure configuration
│
├── workspace-agent/            # Agent-related components
│
├── workspace-app/
│   ├── web/                   # Frontend application
│   └── pricing/               # Pricing-related components
│
├── workspace-ml/
│   ├── data/
│   │   └── raw/               # Downloaded datasets (not committed)
│   │
│   ├── training/
│   │   └── disease/
│   │       ├── dataset.py     # Dataset loading
│   │       ├── augment.py     # Image augmentation
│   │       ├── train.py       # Model training
│   │       ├── calibrate.py   # Confidence calibration
│   │       └── export_onnx.py # ONNX export
│   │
│   ├── ml_service/
│   │   ├── inference/
│   │   │   ├── disease_onnx.py
│   │   │   └── gradcam.py
│   │   ├── models/            # Model artifacts
│   │   ├── loader.py          # Model loading
│   │   └── api.py             # ML integration interface
│   │
│   ├── scripts/               # Supporting scripts
│   ├── reports/               # Evaluation reports
│   ├── requirements.in       # ML dependency declarations
│   └── CLAUDE.md              # AI coding instructions
│
├── .env.example               # Environment-variable template
├── .gitignore
└── README.md
```

Some files and directories are placeholders and will be implemented during development.

## ⚙️ Local Setup

### 1. Prerequisites

- Git
- Python 3.13
- VS Code recommended

### 2. Clone the repository

```powershell
git clone https://github.com/CoderAryan29/HACKSHIFT-IITD-SNACKOVERFLOW.git
cd HACKSHIFT-IITD-SNACKOVERFLOW
```

### 3. Create a virtual environment

```powershell
py -3.13 -m venv venv
```

### 4. Activate the environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install ML dependencies

The ML dependency manifest is still being prepared. Once `workspace-ml/requirements.in` contains the approved dependencies, install them with:

```powershell
python -m pip install -r workspace-ml/requirements.in
```

Until then, install the required packages explicitly according to the development instructions.

## 📊 Dataset and Evaluation

The planned datasets are:

- **New Plant Diseases:** Primary training dataset.
- **PlantDoc:** Field-style images for additional evaluation.

The initial demonstration will focus on tomato and potato classes.

Dataset splits must be handled carefully to prevent data leakage. Evaluation will include:

- Top-1 accuracy
- Macro-F1 score
- Confusion matrix
- Performance on unseen field-style images
- Examples of successful and unsuccessful predictions

No accuracy claims are made until the corresponding experiments have been run.

## 🔌 ML Integration

The planned Python ML interface includes:

- `load_models()` to load the required model artifacts.
- `predict_disease(image_bytes, crop_hint)` to predict a disease from an image.
- `model_info()` to expose model metadata.

Predictions are intended to include the leading classes, confidence scores, model version, and confidence-gate result.

The inference module is intended to run within the Python backend rather than as a separate HTTP microservice.

## 📦 Model Artifacts

The planned model artifacts are:

- `disease.onnx`: Exported trained model.
- `labels.json`: Class identifiers and label metadata.
- `metrics.json`: Measured evaluation results.

These files must contain valid generated artifacts before being used in production. Model weights, large datasets, credentials, and secrets must not be committed to Git.

## 🌿 Git Workflow

Use a separate branch for each task.

Example:

```powershell
git switch -c ml/disease-model
```

Check your changes:

```powershell
git status
git diff
```

Stage and commit only the intended files:

```powershell
git add path/to/file.py
git commit -m "Implement disease model training"
```

Push your branch:

```powershell
git push -u origin ml/disease-model
```

Open a pull request for review before merging into `main`. Coordinate shared interfaces with teammates before changing contracts.

## 👥 Development Principles

- Keep training code separate from inference code.
- Keep datasets, model weights, and secrets out of Git.
- Evaluate on unseen data.
- Document model limitations and failure cases.
- Avoid claiming unverified performance.
- Keep changes small and reviewable.

## 🚀 Current Milestone

**Milestone 1: ML environment and dataset preparation**

- [x] Set up the Python virtual environment.
- [x] Install and verify the core ML libraries.
- [ ] Download and inspect the datasets.
- [ ] Implement the dataset loader.
- [ ] Train and evaluate the first baseline model.
- [ ] Export and verify the ONNX model.
- [ ] Integrate inference with the application.

