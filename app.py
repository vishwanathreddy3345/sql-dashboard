from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"


def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def login_required(func):
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def home():
    return redirect(url_for("login"))


# 🏠 DASHBOARD
@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db_connection()

    total_employees = conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    total_departments = conn.execute("SELECT COUNT(DISTINCT department) FROM employees").fetchone()[0]
    avg_salary = conn.execute("SELECT AVG(salary) FROM employees").fetchone()[0]
    max_salary = conn.execute("SELECT MAX(salary) FROM employees").fetchone()[0]

    dept_stats = conn.execute("""
        SELECT department, COUNT(*) AS employee_count, AVG(salary) AS avg_salary
        FROM employees
        GROUP BY department
    """).fetchall()

    # ✅ FIX FOR CHARTS
    dept_labels = [row["department"] for row in dept_stats]
    dept_counts = [row["employee_count"] for row in dept_stats]
    dept_avg_salaries = [round(row["avg_salary"], 2) for row in dept_stats]

    conn.close()

    return render_template(
        "index.html",
        total_employees=total_employees,
        total_departments=total_departments,
        avg_salary=round(avg_salary, 2) if avg_salary else 0,
        max_salary=max_salary if max_salary else 0,
        dept_labels=dept_labels,
        dept_counts=dept_counts,
        dept_avg_salaries=dept_avg_salaries
    )


# 👥 EMPLOYEES
@app.route("/employees")
@login_required
def employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM employees").fetchall()
    conn.close()

    return render_template("employees.html", employees=employees)


# 🔍 ✅ FIX FOR YOUR ERROR
@app.route("/employee/<int:id>")
@login_required
def employee_detail(id):
    conn = get_db_connection()
    employee = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    conn.close()

    if not employee:
        return "Employee not found", 404

    return render_template("employee_detail.html", employee=employee)


# ➕ ADD
@app.route("/add-employee", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO employees (name, department, role, salary, city)
            VALUES (?, ?, ?, ?, ?)
        """, (
            request.form["name"],
            request.form["department"],
            request.form["role"],
            request.form["salary"],
            request.form["city"]
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("employees"))

    return render_template("add_employee.html")


# ✏️ EDIT
@app.route("/edit-employee/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    conn = get_db_connection()

    if request.method == "POST":
        conn.execute("""
            UPDATE employees
            SET name=?, department=?, role=?, salary=?, city=?
            WHERE id=?
        """, (
            request.form["name"],
            request.form["department"],
            request.form["role"],
            request.form["salary"],
            request.form["city"],
            id
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("employees"))

    employee = conn.execute("SELECT * FROM employees WHERE id=?", (id,)).fetchone()
    conn.close()

    return render_template("edit_employee.html", employee=employee)


# ❌ DELETE
@app.route("/delete-employee/<int:id>")
@login_required
def delete_employee(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM employees WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("employees"))


if __name__ == "__main__":
    app.run(debug=True)