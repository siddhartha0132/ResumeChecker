# EV Hiring Platform — Frontend v2 (Dual Portal)

This is the **new dual-interface frontend** for the EV Hiring Platform.

## Structure

```
src/
├── App.jsx                        # Landing page + portal router
├── main.jsx
├── index.css
└── components/
    ├── common/                    # Shared components
    │   ├── EVLogo.jsx             # Animated SVG EV logo
    │   ├── LoadingScooter.jsx     # Animated scooter progress bar
    │   └── ParticleField.jsx      # Three.js particle background
    ├── candidate/                 # Candidate Portal (applicant side)
    │   ├── CandidatePortal.jsx    # Main portal with step flow
    │   ├── CompanyDebrief.jsx     # Typing animation welcome screen
    │   ├── RoleSelector.jsx       # 6 EV role cards
    │   ├── ResumeUploader.jsx     # PDF upload with scooter animation
    │   └── ScoreDisplay.jsx       # Results with circular score + PDF export
    └── manager/                   # HR Manager Dashboard
        ├── ManagerDashboard.jsx   # Main dashboard (3 tabs)
        ├── RoleFilter.jsx         # Filter by EV role
        ├── CandidateCard.jsx      # Card with score tooltip
        ├── ResumeViewer.jsx       # Full candidate detail modal
        ├── ComparisonView.jsx     # Side-by-side comparison (up to 4)
        └── ShortlistPanel.jsx     # Shortlist table + CSV/PDF export
```

## Running

```bash
npm install
npm run dev
# Runs on http://localhost:3001
# Proxies /api → http://localhost:5001 (Flask backend)
```

## Features

- **Landing page** — choose Candidate Portal or HR Dashboard
- **Candidate Portal** — 4-step flow: Welcome → Role → Upload → Results
- **HR Dashboard** — Rankings, Shortlist, Upload tabs
- **Score breakdown tooltip** — hover match % to see TF-IDF / Skill / Experience split
- **Side-by-side comparison** — select up to 4 candidates
- **PDF + CSV export** — from both candidate results and shortlist panel
- **Animated scooter** — progress bar during resume analysis
- **Three.js particles** — background on landing and candidate portal
