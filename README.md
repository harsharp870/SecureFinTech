# SecureFinTech

## AI-Powered Fraud Detection & Cybersecurity for Digital Payments

SecureFinTech is a simulated digital-payment security platform that evaluates outgoing P2P transactions using a hybrid fraud-risk engine. The system combines deterministic security rules with an Isolation Forest machine-learning model and presents an explainable risk decision to the user.

> **Current status:** Phase 6 completed and pushed to GitHub. Final demo validation completed.

## Core Features

- User authentication and protected portal
- Simulated wallet with a $10,000 demo balance
- P2P money-transfer workflow
- Transaction validation and recipient checks
- Hybrid fraud-risk scoring
- Deterministic risk rules
- Isolation Forest anomaly detection
- Explainable risk attribution
- APPROVED / FLAGGED transaction decisions
- Transaction history
- Frontend security-status dashboard
- Git-based project versioning

## Fraud Detection Logic

The current Phase 6 implementation combines:

1. **Deterministic Rules (60%)**
   - High transfer amount
   - Rapid successive transactions
   - Account-drain behavior

2. **ML Isolation Forest (40%)**
   - Used for anomaly detection
   - Helps identify transaction behavior that differs from expected patterns

The UI exposes the resulting score and the factors that contributed to a flagged decision.

## Demonstrated Test Cases

### Low-risk transaction
- Amount: $100
- Risk score: approximately 18.7/100
- Result: APPROVED

### High-risk transaction
- Amount: $9,000
- Risk score: 76.5/100
- Result: FLAGGED
- Triggered factors shown in the UI:
  - HIGH_AMOUNT_ELEVATED (+40)
  - RAPID_SUCCESSION (+30)
  - ACCOUNT_DRAIN (+25)

The final composite score is capped/normalized by the application's scoring logic, producing 76.5/100 for the demonstrated case.

## High-Level Architecture

Frontend (React/TypeScript) → Backend API (Python/FastAPI-style service) → Fraud Engine → Rules + Isolation Forest → Decision + Explainability → Database / Transaction History.

See `architecture.png`.

## Project Structure

```text
SecureFinTech/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
├── frontend/
│   └── src/
│       ├── components/
│       └── context/
├── architecture.png
├── project_report.docx
├── SecureFinTech_Presentation.pptx
├── demo_script.md
└── final_review_checklist.md
```

## Running the Project

### Backend

Activate the Python virtual environment and start the backend using the command configured for the project.

Example:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
```

Then use the project's configured backend start command.

### Frontend

```powershell
cd frontend
npm install
```

Then use the project's configured frontend development command.

> Do not commit local databases, virtual environments, `node_modules`, build output, or Python cache files. The repository `.gitignore` already excludes these categories.

## Security Considerations

- Passwords should never be stored in plaintext.
- Secrets should be supplied through environment variables.
- Database files used for local demos should not be committed.
- Authentication and authorization should be enforced server-side.
- Transaction decisions should be logged for auditability.
- ML decisions should be explainable enough for reviewers to understand why a transaction was flagged.

## Future Enhancements

- Real payment gateway sandbox integration
- Real-time streaming fraud detection
- Feature store and model versioning
- Model performance metrics (precision, recall, F1, ROC-AUC)
- Threshold calibration using a labeled dataset
- Device fingerprinting
- IP/geolocation risk signals
- Admin investigation workflow
- Automated alerts
- Model monitoring and drift detection

## Authors

SecureFinTech student project — RNS Institute of Technology, CSE (Cybersecurity).
