# generate_data.py
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# ── USERS ────────────────────────────────────────────────
N_USERS = 2000

GRADE_WEIGHTS = {6: 0.05, 7: 0.05, 8: 0.08, 9: 0.12, 10: 0.20, 11: 0.25, 12: 0.25}
DEVICE_CHOICES = ["android", "ios", "web"]
DEVICE_WEIGHTS = [0.55, 0.25, 0.20]
CURRICULUM_CHOICES = ["CBSE", "ICSE", "JEE", "NEET", "State Board"]
CURRICULUM_WEIGHTS = [0.35, 0.15, 0.20, 0.15, 0.15]
TARGET_EXAM_CHOICES = ["JEE", "NEET", "Boards", "undeclared"]
TARGET_EXAM_WEIGHTS = [0.30, 0.20, 0.30, 0.20]

# Seasonality: weight signups by month (Feb-Apr, Sep-Nov are exam-prep peaks)
MONTH_WEIGHTS = {1: 0.06, 2: 0.11, 3: 0.13, 4: 0.11, 5: 0.05, 6: 0.04,
                 7: 0.05, 8: 0.06, 9: 0.11, 10: 0.13, 11: 0.10, 12: 0.05}

def random_signup_date(year=2025):
    month = np.random.choice(list(MONTH_WEIGHTS.keys()), p=list(MONTH_WEIGHTS.values()))
    day = random.randint(1, 28)  # avoid month-length edge cases
    return datetime(year, month, day).date()

users = []
for user_id in range(1, N_USERS + 1):
    grade = np.random.choice(list(GRADE_WEIGHTS.keys()), p=list(GRADE_WEIGHTS.values()))
    device = np.random.choice(DEVICE_CHOICES, p=DEVICE_WEIGHTS)
    curriculum = np.random.choice(CURRICULUM_CHOICES, p=CURRICULUM_WEIGHTS)
    target_exam = np.random.choice(TARGET_EXAM_CHOICES, p=TARGET_EXAM_WEIGHTS)
    is_test_account = random.random() < 0.05
    signup_date = random_signup_date()

    users.append({
        "user_id": user_id,
        "signup_date": signup_date,
        "grade": int(grade),
        "device": device,
        "curriculum": curriculum,
        "target_exam": target_exam,
        "is_test_account": is_test_account,
    })

users_df = pd.DataFrame(users)

# ── SESSIONS ─────────────────────────────────────────────
N_SESSIONS = 15000

GOAL_RANGES = {
    "deep_study": (60, 120),
    "revision": (30, 60),
    "quick_quiz": (15, 30),
}
GOAL_CHOICES = list(GOAL_RANGES.keys())
GOAL_WEIGHTS = [0.35, 0.40, 0.25]  # deep_study, revision, quick_quiz

MISMATCH_RATE = 0.05

# Power-law-ish user activity: sample weights from an exponential distribution
user_activity_weights = np.random.exponential(scale=1.0, size=N_USERS)
user_activity_probs = user_activity_weights / user_activity_weights.sum()

def random_time_in_2025():
    start = datetime(2025, 1, 1)
    end = datetime(2025, 12, 28, 23, 59)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)

sessions = []
for session_id in range(1, N_SESSIONS + 1):
    user_id = int(np.random.choice(users_df["user_id"], p=user_activity_probs))
    goal = np.random.choice(GOAL_CHOICES, p=GOAL_WEIGHTS)
    is_mismatch = random.random() < MISMATCH_RATE

    if is_mismatch:
        # pull duration from a DIFFERENT goal's range
        other_goals = [g for g in GOAL_CHOICES if g != goal]
        mismatch_goal = random.choice(other_goals)
        low, high = GOAL_RANGES[mismatch_goal]
    else:
        low, high = GOAL_RANGES[goal]

    duration = round(random.uniform(low, high), 1)
    start_time = random_time_in_2025()

    sessions.append({
        "session_id": session_id,
        "user_id": user_id,
        "start_time": start_time,
        "duration_minutes": duration,
        "session_goal": goal,
        "is_duration_mismatch": is_mismatch,
    })

sessions_df = pd.DataFrame(sessions)

# ── EVENTS ───────────────────────────────────────────────
N_EVENTS = 40000

EVENT_TYPES = ["lesson_started", "lesson_completed", "quiz_submitted",
               "video_completed", "doubt_raised"]
EVENT_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]

# Sample session_id proportional to duration_minutes (longer sessions get more events)
session_weights = sessions_df["duration_minutes"].values
session_probs = session_weights / session_weights.sum()

events = []
for event_id in range(1, N_EVENTS + 1):
    session_row = sessions_df.iloc[np.random.choice(len(sessions_df), p=session_probs)]
    session_id = int(session_row["session_id"])
    session_start = session_row["start_time"]
    session_duration = session_row["duration_minutes"]

    event_type = np.random.choice(EVENT_TYPES, p=EVENT_WEIGHTS)
    offset_minutes = random.uniform(0, session_duration)
    event_timestamp = session_start + timedelta(minutes=offset_minutes)

    events.append({
        "event_id": event_id,
        "session_id": session_id,
        "event_type": event_type,
        "timestamp": event_timestamp,
    })

events_df = pd.DataFrame(events)

# ── SAVE TO CSV ──────────────────────────────────────────
users_df.to_csv("users.csv", index=False)
sessions_df.to_csv("sessions.csv", index=False)
events_df.to_csv("events.csv", index=False)

print(f"Generated {len(users_df)} users, {len(sessions_df)} sessions, {len(events_df)} events.")
print(f"Test accounts: {users_df['is_test_account'].sum()} ({users_df['is_test_account'].mean()*100:.1f}%)")
print(f"Duration mismatches: {sessions_df['is_duration_mismatch'].sum()} ({sessions_df['is_duration_mismatch'].mean()*100:.1f}%)")