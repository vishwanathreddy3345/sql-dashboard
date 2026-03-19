import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Drop old table if needed
cursor.execute("DROP TABLE IF EXISTS employees")

# Create employees table
cursor.execute("""
CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department TEXT NOT NULL,
    role TEXT NOT NULL,
    salary INTEGER NOT NULL,
    city TEXT NOT NULL
)
""")

# Sample data
employees_data = [
    ("Aarav Sharma", "Engineering", "Software Engineer", 60000, "Bengaluru"),
    ("Priya Reddy", "Engineering", "Backend Developer", 75000, "Hyderabad"),
    ("Rohan Mehta", "HR", "HR Manager", 50000, "Mumbai"),
    ("Sneha Iyer", "Marketing", "Marketing Executive", 45000, "Chennai"),
    ("Kiran Kumar", "Engineering", "Data Analyst", 70000, "Bengaluru"),
    ("Neha Singh", "Finance", "Accountant", 55000, "Delhi"),
    ("Vikram Rao", "Engineering", "DevOps Engineer", 80000, "Pune"),
    ("Anjali Das", "Marketing", "SEO Specialist", 48000, "Kolkata"),
    ("Rahul Verma", "Finance", "Financial Analyst", 62000, "Noida"),
    ("Meera Nair", "HR", "Recruiter", 43000, "Bengaluru")
]

cursor.executemany("""
INSERT INTO employees (name, department, role, salary, city)
VALUES (?, ?, ?, ?, ?)
""", employees_data)

conn.commit()
conn.close()

print("Database and employees table created successfully.")