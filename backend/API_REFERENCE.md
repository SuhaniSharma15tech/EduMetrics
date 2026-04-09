# EduMetrics Backend — API Reference

Base URL: `http://localhost:8000` (dev) / `https://your-deploy.railway.app` (prod)

All analysis endpoints live under `/api/analysis/`.  
Authentication: JWT Bearer token (obtain via `POST /api/login/`).

---

## Auth

### Login
```
POST /api/login/
Body: { "email": "...", "password": "..." }
Returns: { "access": "<jwt>", "refresh": "<jwt>" }
```

### Refresh Token
```
POST /api/token/refresh/
Body: { "refresh": "<jwt>" }
```

### Logout
```
POST /api/logout/
Body: { "refresh": "<jwt>" }
```

---

## Dashboard

### Stat Cards
```
GET /api/analysis/dashboard/summary/?class_id=CS2024A&semester=1&sem_week=9
```
Returns the 4 stat cards:
```json
{
  "total_students": 40,
  "avg_risk_score": 72.5,
  "flagged_this_week": 6,
  "interventions_this_week": 3,
  "risk_breakdown": { "critical": 2, "watch": 3, "warning": 1, "safe": 34 }
}
```

---

## Flagged Students  *(matches FLAGGED[] in app.js)*
```
GET /api/analysis/flagged/?class_id=CS2024A&semester=1&sem_week=9
```
Each item:
```json
{
  "id": "STU2024001",
  "name": "Aryan Mehta",
  "roll": "STU2024001",
  "avatar": "AM",
  "risk": "high",
  "reason": "Severe Absenteeism | Stopped Submitting",
  "academicPerf": 43.0,
  "effortScore": 38.0,
  "attendRecent": 42.0,
  "quizSubmit": 45.0,
  "quizAvg": 42.1,
  "assignAvg": 60.3,
  "riskFail": 78,
  "midterm": "Predicted: 62.0%",
  "avgRisk": 78,
  "avgEt": 55.0,
  "avgAt": 45.0,
  "overallAttend": 42.0,
  "riskDetention": 54,
  "recovery": 22,
  "weekEt": [72, 68, 62, 58, 55, 50, 46, 42, 38],
  "weekAt": [80, 75, 65, 60, 55, 50, 48, 45, 43],
  "classAvgEt": 65.0,
  "classAvgPerf": 70.0,
  "studentAvgEt": 55.0,
  "studentAvgPerf": 55.0,
  "etThisWeek": 38.0,
  "perfThisWeek": 43.0,
  "factors": [
    {"label": "Severe Absenteeism", "pct": 85, "color": "#ef4444"},
    {"label": "Stopped Submitting", "pct": 62, "color": "#f59e0b"}
  ],
  "majorFactor": "Severe Absenteeism",
  "flagHistory": [
    {"date": "Week 5", "diagnosis": "Low Attendance", "intervened": true},
    {"date": "Week 9", "diagnosis": "Severe Absenteeism | Stopped Submitting", "intervened": false}
  ]
}
```

---

## All Students Roster  *(matches ALL_STUDENTS[] in app.js)*
```
GET /api/analysis/students/?class_id=CS2024A&semester=1&sem_week=9
```
Each item:
```json
{
  "id": "STU2024001",
  "name": "Aryan Mehta",
  "roll": "STU2024001",
  "avatar": "AM",
  "academicPerf": 43.0,
  "riskScore": 78,
  "effort": 38.0,
  "engagement": 43.5,
  "predMidterm": 62.0,
  "predEndterm": 58.0,
  "attendance": 42.0,
  "riskLevel": "high"
}
```

---

## Student Detail (deep-dive)
```
GET /api/analysis/student/STU2024001/detail/?semester=1&sem_week=9
```

## Student Trajectory (line chart)
```
GET /api/analysis/student/STU2024001/trajectory/?semester=1&from_week=1
```
Returns:
```json
{
  "weeks": ["W1","W2","W3","W4","W5","W6","W7","W8","W9"],
  "effort": [72, 68, 62, 58, 55, 50, 46, 42, 38],
  "performance": [80, 76, 70, 66, 62, 58, 54, null, 43],
  "attendance": [80.0, 75.0, 65.0, 60.0, 55.0, 50.0, 48.0, 45.0, 43.0],
  "quiz": [...],
  "assignment": [...]
}
```

---

## Class Analytics (analytics page)
```
GET /api/analysis/analytics/?class_id=CS2024A&semester=1&sem_week=9
```
Returns `scatter[]`, `heatmap[]`, and `weekly_averages[]` for Chart.js.

---

## Last Week Comparison  *(matches LAST_WEEK[] in app.js)*
```
GET /api/analysis/last_week/?class_id=CS2024A&semester=1&sem_week=9
```
Returns students who were flagged last week with delta values:
`etCurr`, `etPrev`, `atCurr`, `atPrev`, `riskCurr`, `riskPrev`

---

## Predictions

### Pre-Midterm
```
GET /api/analysis/pre_mid_term/?class_id=X&semester=Y&sem_week=6
GET /api/analysis/pre_mid_term/student/?student_id=X&semester=Y
```

### Pre-Endterm
```
GET /api/analysis/pre_end_term/?class_id=X&semester=Y
GET /api/analysis/pre_end_term/student/?student_id=X&semester=Y
```

### Risk of Failing
```
GET /api/analysis/risk_of_failing/?class_id=X&semester=Y&sem_week=10
GET /api/analysis/risk_of_failing/student/?student_id=X&semester=Y
```

### Pre-Semester Watchlist
```
GET /api/analysis/pre_sem_watchlist/?class_id=X&target_semester=2
GET /api/analysis/pre_sem_watchlist/student/?student_id=X&target_semester=2
```

---

## Internal

### Run Analysis Pipeline (called by simulator)
```
POST /api/analysis/trigger_calibrate/
Header: X-Internal-Secret: <value from .env INTERNAL_SECRET>
```
Returns: `{ "action": "advance", "weeks_processed": 2, "elapsed_ms": 1240 }`

### Health Check
```
GET /health/
Returns: { "status": "ok" }
```

---

## Wiring the Frontend

The frontend (app.js) currently uses static mock arrays.
To connect to this API, replace e.g.:

```js
// BEFORE (static mock)
const FLAGGED = [ {...}, {...} ];

// AFTER (live API)
const BASE = 'http://localhost:8000/api/analysis';
const token = localStorage.getItem('access_token');

async function loadFlagged(classId, semester, semWeek) {
  const res = await fetch(
    `${BASE}/flagged/?class_id=${classId}&semester=${semester}&sem_week=${semWeek}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return res.json();  // returns the same shape as FLAGGED[]
}
```

Every response field name matches exactly what app.js expects — no reshaping needed.
