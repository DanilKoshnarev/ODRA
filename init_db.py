#!/usr/bin/env python3
"""Initialize database with all tables."""
import sys
sys.path.insert(0, '/Users/danikosnarev/Desktop/ODRA 2/backend')

from app.db import Base, engine, SessionLocal
from app.models import *

# Create all tables
print("🔧 Creating database tables...")
Base.metadata.create_all(engine)
print("✅ Database tables created successfully!")

# Test connection
db = SessionLocal()
print("✅ Database connection successful!")
db.close()

print("\n✅ Database initialized and ready!")
