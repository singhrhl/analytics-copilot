# load_data.py
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

# Use your MAIN postgres connection here (not agent_readonly) — this needs write access
DATABASE_URL = os.getenv("SUPABASE_ADMIN_URL")  # postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres

engine = create_engine(DATABASE_URL)

users_df = pd.read_csv("users.csv", keep_default_na=False, na_values=[])
sessions_df = pd.read_csv("sessions.csv", keep_default_na=False, na_values=[])
events_df = pd.read_csv("events.csv", keep_default_na=False, na_values=[])

# Order matters: parents before children (FK constraints)
users_df.to_sql("users", engine, if_exists="append", index=False, method="multi", chunksize=500)
print(f"Loaded {len(users_df)} users.")

sessions_df.to_sql("sessions", engine, if_exists="append", index=False, method="multi", chunksize=500)
print(f"Loaded {len(sessions_df)} sessions.")

events_df.to_sql("events", engine, if_exists="append", index=False, method="multi", chunksize=500)
print(f"Loaded {len(events_df)} events.")

print("Done.")