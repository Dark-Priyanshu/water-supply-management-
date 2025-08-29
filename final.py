
import os
import sys
import csv
import sqlite3
from datetime import datetime, date, time, timedelta
from contextlib import contextmanager
from typing import Optional, Tuple, List, Any
from PyQt5.QtCore import QSettings, Qt, QDate, QTime, QDateTime
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QApplication, QDialog, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPushButton, QTabWidget, QTableView,
    QToolBar, QVBoxLayout, QWidget, QFileDialog, QComboBox, QDateEdit, QTimeEdit,
    QSpinBox, QGroupBox, QTextEdit, QHeaderView, QAbstractItemView
)
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQueryModel, QSqlQuery
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PyQt5.QtWidgets import QAction

# ---------- Constants ----------
DB_NAME = "app.db"
DEFAULT_RATE = 125.0  # ₹ per hour
APP_NAME = "Water Supply Manager"
VERSION = "1.0"
CONTACT = "priyanshushakya@proton.me"

# ---------- Optional XLSX support ----------
try:
    import openpyxl  # type: ignore
    HAS_XLSX = True
except ImportError:
    HAS_XLSX = False

# ---------- Database Connection Pool ----------
class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._connection = None
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(DB_NAME)
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.fetchall()
    
    def execute_single(self, query: str, params: Tuple = ()) -> Optional[Tuple]:
        """Execute a query and return single result"""
        results = self.execute_query(query, params)
        return results[0] if results else None

db_manager = DatabaseManager()

# ---------- Optimized Stylesheet ----------
# Light mode stylesheet
light_stylesheet = """
QWidget { 
    background-color: #f5f5f5; 
    color: #333333; 
    font-size: 10.5pt; 
}
QPushButton {
    background-color: #ffffff; 
    color: #333333;
    border: 1px solid #cccccc; 
    border-radius: 4px; 
    min-width: 80px;
}
QPushButton:hover { 
    background-color: #e6f3ff; 
    border-color: #0078d7;
}
QPushButton:pressed {
    background-color: #0078d7;
    color: white;
}
QPushButton:checked {
    background-color: #0078d7;
    color: white;
    border-color: #0078d7;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {
    background-color: #ffffff; 
    color: #333333;
    border: 1px solid #cccccc; 
    border-radius: 4px;
}
QTableView {
    background-color: #ffffff; 
    alternate-background-color: #f9f9f9;
    gridline-color: #cccccc; 
    color: #333333;
    selection-background-color: #0078d7; 
    selection-color: white;
}
QHeaderView::section {
    background-color: #e6e6e6; 
    color: #333333;
    border: 1px solid #cccccc; 
    padding: 4px;
}
QToolBar { 
    background-color: #f0f0f0; 
    border-bottom: 2px solid #0078d7;
    spacing: 5px;
    padding: 2px;
}
QToolBar QPushButton {
    margin: 2px;
}
QMenuBar, QMenu { 
    background-color: #f0f0f0; 
    color: #333333; 
}
QMenu::item:selected { 
    background-color: #0078d7; 
    color: white;
}
QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: #f5f5f5;
}
QTabBar::tab {
    background: #e6e6e6;
    color: #333333;
    border: 1px solid #cccccc;
    border-bottom-color: #f5f5f5;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: bold;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background: #ffffff;
    color: #333333;
    border-bottom-color: #ffffff;
}
QGroupBox {
    font-weight: bold;
    border: 2px solid #cccccc;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}
"""

# Dark mode stylesheet
dark_stylesheet = """
QWidget { 
    background-color: #2b2b2b; 
    color: #f0f0f0; 
    font-size: 10.5pt; 
}
QPushButton {
    background-color: #3c3f41; 
    color: #f0f0f0;
    border: 1px solid #5c5c5c; 
    border-radius: 4px; 
    padding: 8px 12px;
    font-weight: bold;
    min-width: 80px;
}
QPushButton:hover { 
    background-color: #505354; 
    border-color: #0078d7;
}
QPushButton:pressed {
    background-color: #0078d7;
    color: white;
}
QPushButton:checked {
    background-color: #0078d7;
    color: white;
    border-color: #0078d7;
}
QLineEdit, QComboBox, QDateEdit, QTimeEdit, QTextEdit {
    background-color: #3c3f41; 
    color: #f0f0f0;
    border: 1px solid #5c5c5c; 
    border-radius: 4px;
}
QTableView {
    background-color: #3c3f41; 
    alternate-background-color: #2e2e2e;
    gridline-color: #5c5c5c; 
    color: #f0f0f0;
    selection-background-color: #0078d7; 
    selection-color: white;
}
QHeaderView::section {
    background-color: #444; 
    color: #fff;
    border: 1px solid #5c5c5c; 
    padding: 4px;
}
QToolBar { 
    background-color: #2e2e2e; 
    border-bottom: 2px solid #0078d7;
    spacing: 8px;
    padding: 4px;
}
QToolBar QPushButton {
    margin: 2px;
}
QMenuBar, QMenu { 
    background-color: #2e2e2e; 
    color: #f0f0f0; 
}
QMenu::item:selected { 
    background-color: #0078d7; 
}
QTabWidget::pane {
    border: 1px solid #444;
    background-color: #2b2b2b;
}
QTabBar::tab {
    background: #3c3f41;
    color: #dcdcdc;
    padding: 8px 15px;
    border: 1px solid #5c5c5c;
    border-bottom-color: #2b2b2b;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: bold;
}
QTabBar::tab:selected, QTabBar::tab:hover {
    background: #505354;
    color: #ffffff;
    border-bottom-color: #505354;
}
QGroupBox {
    font-weight: bold;
    border: 2px solid #5c5c5c;
    border-radius: 6px;
    margin-top: 10px;
    padding-top: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px 0 5px;
}
"""

# These functions will be moved to the MainWindow class


# ---------- Database bootstrap ----------
def ensure_database():
    created = not os.path.exists(DB_NAME)
    with db_manager.get_connection() as conn:
        c = conn.cursor()

        # Users
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'admin'
            );
            """
        )

        # Customers (Farmers)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                village TEXT,
                phone TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

        # Supplies (Water supply records)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supply_date TEXT NOT NULL,           -- 'YYYY-MM-DD'
                customer_id INTEGER NOT NULL,
                crop TEXT,
                start_time TEXT NOT NULL,            -- 'HH:MM'
                end_time   TEXT NOT NULL,            -- 'HH:MM'
                hours REAL NOT NULL DEFAULT 0,       -- auto calc (in hours, decimals)
                amount REAL NOT NULL DEFAULT 0,      -- hours * rate
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(customer_id) REFERENCES customers(id)
            );
            """
        )

        # Migrate existing database to remove rate column if it exists
        try:
            c.execute("PRAGMA table_info(supplies)")
            columns = [col[1] for col in c.fetchall()]
            if 'rate' in columns:
                print("Migrating database: Removing rate column...")
                # Create new table without rate column
                c.execute("""
                    CREATE TABLE supplies_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        supply_date TEXT NOT NULL,
                        customer_id INTEGER NOT NULL,
                        crop TEXT,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL,
                        hours REAL NOT NULL DEFAULT 0,
                        amount REAL NOT NULL DEFAULT 0,
                        notes TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(customer_id) REFERENCES customers(id)
                    )
                """)
                # Copy data without rate column
                c.execute("""
                    INSERT INTO supplies_new (id, supply_date, customer_id, crop, start_time, end_time, hours, amount, notes, created_at)
                    SELECT id, supply_date, customer_id, crop, start_time, end_time, hours, amount, notes, created_at
                    FROM supplies
                """)
                # Drop old table and rename new one
                c.execute("DROP TABLE supplies")
                c.execute("ALTER TABLE supplies_new RENAME TO supplies")
                print("Database migration completed successfully.")
        except Exception as e:
            print(f"Migration warning: {e}")
            # Continue with application startup even if migration fails

    # Seed admin user if first time
    count = db_manager.execute_single("SELECT COUNT(*) FROM users;")
    if count is None:
        db_manager.execute_query("INSERT INTO users (username, password, role) VALUES (?, ?, ?);", ("admin", "admin", "admin"))

    return created

# ---------- Qt SQL connection ----------
def open_qt_db():
    if QSqlDatabase.contains("qt_sql_default_connection"):
        db = QSqlDatabase.database("qt_sql_default_connection")
    else:
        db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(DB_NAME)
    if not db.open():
        raise RuntimeError("Failed to open database")
    return db

# ---------- Optimized Helpers ----------
def to_hours(start_str: str, end_str: str) -> float:
    """HH:MM or hh:MM AM/PM → hours (float). Handles overnight span."""
    try:
        if "AM" in start_str.upper() or "PM" in start_str.upper():
            fmt = "%I:%M %p"
        else:
            fmt = "%H:%M"
        s = datetime.strptime(start_str.strip(), fmt)
        e = datetime.strptime(end_str.strip(), fmt)
        if e < s:  # Overnight roll
            e += timedelta(days=1)
        delta = e - s
        return round(delta.total_seconds() / 3600.0, 2)
    except Exception as ex:
        print("Time parsing error:", ex)
        return 0.0


def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"₹{amount:.2f}"

def validate_time_range(start_time: str, end_time: str) -> bool:
    """Validate that end time is after start time"""
    try:
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        if end < start:
            end = end.replace(day=end.day + 1)  # Handle overnight
        return (end - start).total_seconds() > 0
    except (ValueError, TypeError):
        return False

def export_rows(headers: List[str], rows: List[List], path: str) -> str:
    """Export data to CSV or Excel format"""
    if path.lower().endswith('.xlsx'):
        if not HAS_XLSX:
            # fallback to csv
            path = os.path.splitext(path)[0] + '.csv'
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(headers)
                w.writerows(rows)
            return path
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(headers)
        for r in rows:
            ws.append(r)
        wb.save(path)
        return path
    
    # CSV
    if not path.lower().endswith('.csv'):
        path += '.csv'
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    return path

def safe_html_value(value) -> str:
    """Safely format a value for HTML output"""
    if value is None:
        return ""
    try:
        # Convert to string and escape HTML characters
        str_val = str(value).strip()
        # Basic HTML escaping
        str_val = str_val.replace("&", "&amp;")
        str_val = str_val.replace("<", "&lt;")
        str_val = str_val.replace(">", "&gt;")
        str_val = str_val.replace('"', "&quot;")
        return str_val
    except Exception:
        return ""

def format_date_for_display(date_str: str) -> str:
    """Format date string for better display"""
    if not date_str:
        return ""
    try:
        # If it's already in YYYY-MM-DD format, convert to DD/MM/YYYY
        if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
            year, month, day = date_str.split('-')
            return f"{day}/{month}/{year}"
        return str(date_str)
    except Exception:
        return str(date_str)

# ---------- SQL Query Templates ----------
SQL_TEMPLATES = {
    'customers_select': "SELECT id, name FROM customers ORDER BY name ASC",
    'customers_insert': "INSERT INTO customers (name, village, phone) VALUES (?,?,?)",
    'customers_update': "UPDATE customers SET name=?, village=?, phone=? WHERE id=?",
    'customers_delete': "DELETE FROM customers WHERE id=?",
    'supplies_insert': """
        INSERT INTO supplies (supply_date, customer_id, crop, start_time, end_time, hours, amount, notes)
        VALUES (?,?,?,?,?,?,?,?)
    """,
    'supplies_update': """
        UPDATE supplies SET supply_date=?, customer_id=?, crop=?, start_time=?, end_time=?,
        hours=?, amount=?, notes=? WHERE id=?
    """,
    'supplies_delete': "DELETE FROM supplies WHERE id=?",
    'supplies_select_base': """
        SELECT s.id, s.supply_date, c.name as farmer, s.crop, s.start_time, s.end_time,
        CAST(s.hours AS INTEGER) as h, CAST((s.hours - CAST(s.hours AS INTEGER)) * 60 AS INTEGER) as m,
        s.amount, s.notes
    """,
    'supplies_sum': "SELECT SUM(amount) FROM supplies WHERE customer_id=? AND supply_date BETWEEN ? AND ?"
}

# ---------- Login Dialog ----------
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Login — {APP_NAME}")
        self.setModal(True)
        self.setFixedWidth(400)
        # Set the application icon
        try:
            self.setWindowIcon(QIcon("assets/sewage-plant.png"))
        except Exception:
            # Fallback to theme icon if custom icon fails
            try:
                self.setWindowIcon(QIcon.fromTheme("applications-utilities"))
            except Exception:
                pass
        self.setup_ui()

    def setup_ui(self):
        """Setup the login UI"""
        form = QFormLayout()
        self.user = QLineEdit()
        self.user.setPlaceholderText("Enter username")
        self.pwd = QLineEdit()
        self.pwd.setEchoMode(QLineEdit.Password)
        self.pwd.setPlaceholderText("Enter password")
        
        form.addRow("Username", self.user)
        form.addRow("Password", self.pwd)

        # Main buttons
        btns = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_cancel = QPushButton("Exit")
        btns.addWidget(self.btn_login)
        btns.addWidget(self.btn_cancel)

        # Additional options
        options_layout = QHBoxLayout()
        self.btn_forgot = QPushButton("Forgot Password")
        self.btn_create = QPushButton("Create User")
        options_layout.addWidget(self.btn_forgot)
        options_layout.addWidget(self.btn_create)

        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)
        root.addLayout(options_layout)

        # Connect signals
        self.btn_login.clicked.connect(self.try_login)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_forgot.clicked.connect(self.show_forgot_password)
        self.btn_create.clicked.connect(self.show_create_user)
        self.user.returnPressed.connect(self.try_login)
        self.pwd.returnPressed.connect(self.try_login)

    def try_login(self):
        """Attempt to login with provided credentials"""
        u = self.user.text().strip()
        p = self.pwd.text().strip()
        
        if not u or not p:
            QMessageBox.warning(self, "Validation", "Please enter both username and password")
            return
            
        try:
            user_data = db_manager.execute_single(
                "SELECT id, role FROM users WHERE username=? AND password=?", 
                (u, p)
            )
            if user_data:
                self.accept()
            else:
                QMessageBox.warning(self, "Login Failed", "Invalid username or password")
                self.pwd.clear()
                self.pwd.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")

    def show_forgot_password(self):
        """Show forgot password dialog"""
        dialog = ForgotPasswordDialog(self)
        dialog.exec_()

    def show_create_user(self):
        """Show create user dialog"""
        dialog = CreateUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, "Success", "User created successfully!")


# ---------- Forgot Password Dialog ----------
class ForgotPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Forgot Password")
        self.setModal(True)
        self.setFixedWidth(350)
        self.setup_ui()

    def setup_ui(self):
        """Setup the forgot password UI"""
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel("Enter your username to reset password:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Form
        form = QFormLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        form.addRow("Username", self.username)
        
        # New password fields
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setPlaceholderText("Enter new password")
        form.addRow("New Password", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm new password")
        form.addRow("Confirm Password", self.confirm_password)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_reset = QPushButton("Reset Password")
        self.btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.btn_reset.clicked.connect(self.reset_password)
        self.btn_cancel.clicked.connect(self.reject)
        self.username.returnPressed.connect(self.reset_password)
        self.new_password.returnPressed.connect(self.reset_password)
        self.confirm_password.returnPressed.connect(self.reset_password)

    def reset_password(self):
        """Reset the user's password"""
        username = self.username.text().strip()
        new_pwd = self.new_password.text().strip()
        confirm_pwd = self.confirm_password.text().strip()
        
        if not username:
            QMessageBox.warning(self, "Validation", "Please enter username")
            self.username.setFocus()
            return
            
        if not new_pwd:
            QMessageBox.warning(self, "Validation", "Please enter new password")
            self.new_password.setFocus()
            return
            
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "Validation", "Passwords do not match")
            self.confirm_password.clear()
            self.confirm_password.setFocus()
            return
            
        if len(new_pwd) < 3:
            QMessageBox.warning(self, "Validation", "Password must be at least 3 characters")
            self.new_password.setFocus()
            return
        
        try:
            # Check if user exists
            user_exists = db_manager.execute_single(
                "SELECT id FROM users WHERE username=?", (username,)
            )
            
            if not user_exists:
                QMessageBox.warning(self, "Error", "Username not found")
                self.username.setFocus()
                return
            
            # Update password
            db_manager.execute_query(
                "UPDATE users SET password=? WHERE username=?", 
                (new_pwd, username)
            )
            
            QMessageBox.information(self, "Success", "Password reset successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset password: {str(e)}")


# ---------- Create User Dialog ----------
class CreateUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New User")
        self.setModal(True)
        self.setFixedWidth(350)
        self.setup_ui()

    def setup_ui(self):
        """Setup the create user UI"""
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel("Create a new user account:")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Form
        form = QFormLayout()
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username")
        form.addRow("Username *", self.username)
        
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Enter password")
        form.addRow("Password *", self.password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm password")
        form.addRow("Confirm Password *", self.confirm_password)
        
        self.role = QComboBox()
        self.role.addItems(["admin", "user"])
        form.addRow("Role", self.role)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton("Create User")
        self.btn_cancel = QPushButton("Cancel")
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        
        # Connect signals
        self.btn_create.clicked.connect(self.create_user)
        self.btn_cancel.clicked.connect(self.reject)
        self.username.returnPressed.connect(self.create_user)
        self.password.returnPressed.connect(self.create_user)
        self.confirm_password.returnPressed.connect(self.create_user)

    def create_user(self):
        """Create a new user"""
        username = self.username.text().strip()
        password = self.password.text().strip()
        confirm_pwd = self.confirm_password.text().strip()
        role = self.role.currentText()
        
        if not username:
            QMessageBox.warning(self, "Validation", "Please enter username")
            self.username.setFocus()
            return
            
        if not password:
            QMessageBox.warning(self, "Validation", "Please enter password")
            self.password.setFocus()
            return
            
        if password != confirm_pwd:
            QMessageBox.warning(self, "Validation", "Passwords do not match")
            self.confirm_password.clear()
            self.confirm_password.setFocus()
            return
            
        if len(username) < 3:
            QMessageBox.warning(self, "Validation", "Username must be at least 3 characters")
            self.username.setFocus()
            return
            
        if len(password) < 3:
            QMessageBox.warning(self, "Validation", "Password must be at least 3 characters")
            self.password.setFocus()
            return
        
        try:
            # Check if username already exists
            existing_user = db_manager.execute_single(
                "SELECT id FROM users WHERE username=?", (username,)
            )
            
            if existing_user:
                QMessageBox.warning(self, "Error", "Username already exists")
                self.username.setFocus()
                return
            
            # Create new user
            db_manager.execute_query(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                (username, password, role)
            )
            
            QMessageBox.information(self, "Success", f"User '{username}' created successfully!")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")

# ---------- Customers Tab ----------
class CustomersTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        self.connect_signals()

    def setup_ui(self):
        """Setup the customers UI"""
        # Table view
        self.view = QTableView()
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Form
        form_box = QGroupBox("Add / Update Farmer")
        form = QFormLayout()
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Enter farmer name")
        self.txt_village = QLineEdit()
        self.txt_village.setPlaceholderText("Enter village name")
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("Enter phone number")
        
        form.addRow("Name *", self.txt_name)
        form.addRow("Village", self.txt_village)
        form.addRow("Phone", self.txt_phone)
        form_box.setLayout(form)

        # Buttons
        btn_add = QPushButton("Add")
        btn_upd = QPushButton("Update")
        btn_del = QPushButton("Delete")
        btn_clr = QPushButton("Clear")

        btn_row = QHBoxLayout()
        for btn in (btn_add, btn_upd, btn_del, btn_clr):
            btn_row.addWidget(btn)

        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.addWidget(form_box)
        layout.addLayout(btn_row)

        # Store button references
        self.btn_add = btn_add
        self.btn_upd = btn_upd
        self.btn_del = btn_del
        self.btn_clr = btn_clr



    def setup_model(self):
        """Setup the table model"""
        self.model = QSqlTableModel(self)
        self.model.setTable("customers")
        self.model.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.model.select()
        
        # Set headers
        headers = ["ID", "Name", "Village", "Phone", "Created"]
        for i, header in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, header)
        
        self.view.setModel(self.model)

    def connect_signals(self):
        """Connect all signals"""
        self.btn_add.clicked.connect(self.add_rec)
        self.btn_upd.clicked.connect(self.upd_rec)
        self.btn_del.clicked.connect(self.del_rec)
        self.btn_clr.clicked.connect(self.clear_form)
        self.view.selectionModel().selectionChanged.connect(self.sync_form)

    def current_id(self) -> Optional[int]:
        """Get the ID of currently selected row"""
        idx = self.view.currentIndex()
        if not idx.isValid():
            return None
        row = idx.row()
        return self.model.data(self.model.index(row, 0))

    def add_rec(self):
        """Add a new customer record"""
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required")
            self.txt_name.setFocus()
            return
            
        village = self.txt_village.text().strip()
        phone = self.txt_phone.text().strip()
        
        try:
            db_manager.execute_query(SQL_TEMPLATES['customers_insert'], (name, village, phone))
            self.model.select()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add customer: {str(e)}")

    def upd_rec(self):
        """Update selected customer record"""
        pk = self.current_id()
        if pk is None:
            QMessageBox.information(self, "Update", "Select a row to update")
            return
            
        name = self.txt_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Validation", "Name is required")
            self.txt_name.setFocus()
            return
            
        village = self.txt_village.text().strip()
        phone = self.txt_phone.text().strip()
        
        try:
            db_manager.execute_query(SQL_TEMPLATES['customers_update'], (name, village, phone, pk))
            self.model.select()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update customer: {str(e)}")

    def del_rec(self):
        """Delete selected customer record"""
        pk = self.current_id()
        if pk is None:
            return
            
        reply = QMessageBox.question(
            self, "Confirm", "Delete selected farmer?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db_manager.execute_query(SQL_TEMPLATES['customers_delete'], (pk,))
                self.model.select()
                self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete customer: {str(e)}")

    def clear_form(self):
        """Clear the form fields"""
        self.txt_name.clear()
        self.txt_village.clear()
        self.txt_phone.clear()
        self.view.clearSelection()
        self.txt_name.setFocus()

    def sync_form(self):
        """Sync form with selected table row"""
        idx = self.view.currentIndex()
        if not idx.isValid():
            return
            
        r = idx.row()
        self.txt_name.setText(str(self.model.data(self.model.index(r, 1)) or ""))
        self.txt_village.setText(str(self.model.data(self.model.index(r, 2)) or ""))
        self.txt_phone.setText(str(self.model.data(self.model.index(r, 3)) or ""))

# ---------- Water Supply Tab ----------
class SupplyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.reload_customers()
        self.refresh_table()

    def build_ui(self):
        # Form
        form_box = QGroupBox("Record Water Supply")
        form = QFormLayout()
        self.dt = QDateEdit()
        self.dt.setCalendarPopup(True)
        self.dt.setDate(QDate.currentDate())
        self.cmb_farmer = QComboBox()
        self.txt_crop = QLineEdit()
        self.t_start = QTimeEdit()
        self.t_start.setDisplayFormat("HH:mm")
        self.t_start.setTime(QTime.currentTime())
        self.t_end = QTimeEdit()
        self.t_end.setDisplayFormat("HH:mm")
        self.t_end.setTime(QTime.currentTime())
        self.txt_hours = QLineEdit()
        self.txt_hours.setReadOnly(True)
        self.txt_amount = QLineEdit()
        self.txt_amount.setReadOnly(True)
        self.txt_notes = QLineEdit()
        self.t_start.setDisplayFormat("HH:mm")
        self.t_end.setDisplayFormat("HH:mm")

        # Auto calculate when time changes
        self.t_start.timeChanged.connect(self.auto_calc)
        self.t_end.timeChanged.connect(self.auto_calc)

        for lbl, w in (
            ("Date", self.dt), ("Farmer", self.cmb_farmer), ("Crop", self.txt_crop),
            ("Pump Start", self.t_start), ("Pump Off", self.t_end), ("Hours", self.txt_hours),
            ("Amount (₹)", self.txt_amount), ("Notes", self.txt_notes)
        ):
            form.addRow(lbl, w)
        form_box.setLayout(form)

        # Buttons
        btn_calc = QPushButton("Auto Calculate")
        btn_add = QPushButton("Add Record")
        btn_upd = QPushButton("Update Selected")
        btn_del = QPushButton("Delete Selected")
        btn_clear = QPushButton("Clear")

        btn_calc.clicked.connect(self.auto_calc)
        btn_add.clicked.connect(self.add_record)
        btn_upd.clicked.connect(self.update_record)
        btn_del.clicked.connect(self.delete_record)
        btn_clear.clicked.connect(self.clear_form)

        btns = QHBoxLayout()
        for b in (btn_calc, btn_add, btn_upd, btn_del, btn_clear):
            btns.addWidget(b)

        # Table (Query model with join to show farmer name)
        self.model = QSqlQueryModel(self)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Layout
        root = QVBoxLayout(self)
        root.addWidget(form_box)
        root.addLayout(btns)
        root.addWidget(self.view)

        # Selection → form sync
        self.view.selectionModel().selectionChanged.connect(self.sync_form)

    def reload_customers(self):
        self.cmb_farmer.clear()
        q = QSqlQuery("SELECT id, name FROM customers ORDER BY name ASC")
        while q.next():
            self.cmb_farmer.addItem(q.value(1), q.value(0))

    def base_select_query(self):
        return (
            "SELECT s.id, s.supply_date, c.name as farmer, s.crop, s.start_time, s.end_time,"
            "CAST(s.hours AS INTEGER) as h, CAST((s.hours - CAST(s.hours AS INTEGER)) * 60 AS INTEGER) as m,"
            "s.amount, s.notes"
        )

    def refresh_table(self):
        sql = self.base_select_query() + " FROM supplies s JOIN customers c ON s.customer_id=c.id ORDER BY s.supply_date DESC, s.id DESC"
        self.model.setQuery(sql)
        headers = ["ID", "Date", "Farmer", "Crop", "Start", "Off", "Hours", "Minutes", "Amount", "Notes"]
        for i, h in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, h)

    def auto_calc(self):
        st = self.t_start.time().toString("HH:mm")
        et = self.t_end.time().toString("HH:mm")
        hrs = to_hours(st, et)
        self.txt_hours.setText(f"{hrs:.2f}")
        rate = DEFAULT_RATE  # Fixed rate
        amt = round(hrs * rate, 2)
        self.txt_amount.setText(f"{amt:.2f}")

    def clear_form(self):
        self.dt.setDate(QDate.currentDate())
        if self.cmb_farmer.count():
            self.cmb_farmer.setCurrentIndex(0)
        self.txt_crop.clear()
        now = QTime.currentTime()
        self.t_start.setTime(now)
        self.t_end.setTime(now)
        self.txt_hours.clear()
        self.txt_amount.clear()
        self.txt_notes.clear()
        self.view.clearSelection()

    def current_row_id(self):
        idx = self.view.currentIndex()
        if not idx.isValid():
            return None
        # first column is id
        return self.model.data(self.model.index(idx.row(), 0))

    def collect_values(self):
        """Collect and validate form values"""
        supply_date = self.dt.date().toString('yyyy-MM-dd')
        customer_id = self.cmb_farmer.currentData()
        crop = self.txt_crop.text().strip()
        st = self.t_start.time().toString('HH:mm')
        et = self.t_end.time().toString('HH:mm')
        
        # Validate time range
        if not validate_time_range(st, et):
            QMessageBox.warning(self, "Validation", "End time must be after start time!")
            return None, None, None, None, None, None, None, None
            
        hrs = to_hours(st, et)
        amt = round(hrs * DEFAULT_RATE, 2)
        
        # Update display fields
        self.txt_hours.setText(f"{hrs:.2f}")
        self.txt_amount.setText(format_currency(amt))
        
        notes = self.txt_notes.text().strip()
        return supply_date, customer_id, crop, st, et, hrs, amt, notes

    def add_record(self):
        """Add a new supply record"""
        values = self.collect_values()
        if values[0] is None:  # Validation failed
            return
            
        d, cid, crop, st, et, hrs, amt, notes = values
        if cid is None:
            QMessageBox.warning(self, "Validation", "Please add/select a Farmer in Customers tab")
            return
            
        try:
            db_manager.execute_query(SQL_TEMPLATES['supplies_insert'], (d, cid, crop, st, et, hrs, amt, notes))
            self.refresh_table()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add record: {str(e)}")

    def update_record(self):
        """Update selected supply record"""
        pk = self.current_row_id()
        if pk is None:
            QMessageBox.information(self, "Update", "Select a row from the table")
            return
            
        values = self.collect_values()
        if values[0] is None:  # Validation failed
            return
            
        d, cid, crop, st, et, hrs, amt, notes = values
        
        try:
            db_manager.execute_query(SQL_TEMPLATES['supplies_update'], (d, cid, crop, st, et, hrs, amt, notes, pk))
            self.refresh_table()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update record: {str(e)}")

    def delete_record(self):
        """Delete selected supply record"""
        pk = self.current_row_id()
        if pk is None:
            return
            
        reply = QMessageBox.question(
            self, "Confirm", "Delete selected record?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                db_manager.execute_query(SQL_TEMPLATES['supplies_delete'], (pk,))
                self.refresh_table()
                self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete record: {str(e)}")

    def sync_form(self):
        idx = self.view.currentIndex()
        if not idx.isValid(): return
        r = idx.row()
        
        d = self.model.data(self.model.index(r,1)); self.dt.setDate(QDate.fromString(d, 'yyyy-MM-dd'))
        farmer_name = self.model.data(self.model.index(r,2))
        # set combo by text
        i = self.cmb_farmer.findText(str(farmer_name))
        if i >= 0: self.cmb_farmer.setCurrentIndex(i)
        self.txt_crop.setText(str(self.model.data(self.model.index(r,3)) or ""))
        self.t_start.setTime(QTime.fromString(self.model.data(self.model.index(r,4)), 'HH:mm'))
        self.t_end.setTime(QTime.fromString(self.model.data(self.model.index(r,5)), 'HH:mm'))
        # Combine hours and minutes for display
        hours = self.model.data(self.model.index(r,6)) or 0
        minutes = self.model.data(self.model.index(r,7)) or 0
        total_hours = float(hours) + float(minutes) / 60.0
        self.txt_hours.setText(f"{total_hours:.2f}")
        self.txt_amount.setText(str(self.model.data(self.model.index(r,8)) or ""))
        self.txt_notes.setText(str(self.model.data(self.model.index(r,9)) or ""))

# ---------- Reports Tab ----------
class ReportsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.reload_customers()
        self.run_query()

    def build_ui(self):
        filters = QGroupBox("Filters")
        grid = QGridLayout()
        self.d_from = QDateEdit()
        self.d_from.setCalendarPopup(True)
        self.d_to = QDateEdit()
        self.d_to.setCalendarPopup(True)
        today = QDate.currentDate()
        self.d_from.setDate(today.addMonths(-1))
        self.d_to.setDate(today)
        self.cmb_farmer = QComboBox()
        self.txt_crop = QLineEdit()
        btn_apply = QPushButton("Apply")
        btn_export = QPushButton("Export…")
        grid.addWidget(QLabel("From"), 0, 0)
        grid.addWidget(self.d_from, 0, 1)
        grid.addWidget(QLabel("To"), 0, 2)
        grid.addWidget(self.d_to, 0, 3)
        grid.addWidget(QLabel("Farmer"), 1, 0)
        grid.addWidget(self.cmb_farmer, 1, 1)
        grid.addWidget(QLabel("Crop"), 1, 2)
        grid.addWidget(self.txt_crop, 1, 3)
        grid.addWidget(btn_apply, 2, 2)
        grid.addWidget(btn_export, 2, 3)
        filters.setLayout(grid)

        self.model = QSqlQueryModel(self)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.lbl_total = QLabel("Total Amount: ₹0.00")

        layout = QVBoxLayout(self)
        layout.addWidget(filters)
        layout.addWidget(self.view)
        layout.addWidget(self.lbl_total)

        btn_apply.clicked.connect(self.run_query)
        btn_export.clicked.connect(self.export_data)

    def reload_customers(self):
        self.cmb_farmer.clear()
        self.cmb_farmer.addItem("(All)", None)
        q = QSqlQuery("SELECT id, name FROM customers ORDER BY name ASC")
        while q.next():
            self.cmb_farmer.addItem(q.value(1), q.value(0))

    def build_sql(self):
        conds = ["s.supply_date BETWEEN :d1 AND :d2"]
        if self.cmb_farmer.currentData() is not None:
            conds.append("s.customer_id = :cid")
        crop = self.txt_crop.text().strip()
        if crop:
            conds.append("s.crop LIKE :crop")
        where = " AND ".join(conds)
        sql = (
            "SELECT s.id, s.supply_date, c.name as farmer, s.crop, s.start_time, s.end_time, "
            "CAST(s.hours AS INTEGER) as h, CAST((s.hours - CAST(s.hours AS INTEGER)) * 60 AS INTEGER) as m, "
            "s.amount, s.notes "
            f"FROM supplies s JOIN customers c ON s.customer_id=c.id WHERE {where} "
            "ORDER BY s.supply_date ASC, s.id ASC"
        )
        return sql

    def run_query(self):
        sql = self.build_sql()
        q = QSqlQuery()
        q.prepare(sql)
        q.bindValue(":d1", self.d_from.date().toString('yyyy-MM-dd'))
        q.bindValue(":d2", self.d_to.date().toString('yyyy-MM-dd'))
        if self.cmb_farmer.currentData() is not None:
            q.bindValue(":cid", self.cmb_farmer.currentData())
        crop = self.txt_crop.text().strip()
        if crop:
            q.bindValue(":crop", f"%{crop}%")
        q.exec_()
        self.model.setQuery(q)
        headers = ["ID", "Date", "Farmer", "Crop", "Start", "Off", "Hours", "Minutes", "Amount", "Notes"]
        for i, h in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, h)
        # total
        tot_sql = self.build_sql().replace("SELECT s.id, s.supply_date, c.name as farmer, s.crop, s.start_time, s.end_time, CAST(s.hours AS INTEGER) as h, CAST((s.hours - CAST(s.hours AS INTEGER)) * 60 AS INTEGER) as m, s.amount, s.notes", "SELECT SUM(s.amount)")
        tot_q = QSqlQuery()
        tot_q.prepare(tot_sql)
        tot_q.bindValue(":d1", self.d_from.date().toString('yyyy-MM-dd'))
        tot_q.bindValue(":d2", self.d_to.date().toString('yyyy-MM-dd'))
        if self.cmb_farmer.currentData() is not None:
            tot_q.bindValue(":cid", self.cmb_farmer.currentData())
        if crop:
            tot_q.bindValue(":crop", f"%{crop}%")
        tot_q.exec_()
        if tot_q.next():
            total = tot_q.value(0) or 0
            self.lbl_total.setText(f"Total Amount: ₹{float(total):.2f}")

    def export_data(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Report", f"report_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmm')}", "CSV (*.csv);;Excel (*.xlsx)")
        if not path:
            return
        headers = [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]
        rows = []
        for r in range(self.model.rowCount()):
            rows.append([self.model.data(self.model.index(r, c)) for c in range(self.model.columnCount())])
        out = export_rows(headers, rows, path)
        QMessageBox.information(self, "Export",f"Exported to{out}")

# ---------- Billing ----------
class BillingTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.build_ui()
        self.reload_customers()
        self.load_data()

    def build_ui(self):
        filt = QGroupBox("Invoice Range")
        g = QGridLayout()
        self.cmb_farmer = QComboBox()
        self.d_from = QDateEdit()
        self.d_from.setCalendarPopup(True)
        self.d_to = QDateEdit()
        self.d_to.setCalendarPopup(True)
        today = QDate.currentDate()
        self.d_from.setDate(today.addDays(-7))
        self.d_to.setDate(today)
        btn_load = QPushButton("Load")
        btn_print = QPushButton("Print Invoice…")
        btn_export = QPushButton("Export…")
        g.addWidget(QLabel("Farmer"), 0, 0)
        g.addWidget(self.cmb_farmer, 0, 1)
        g.addWidget(QLabel("From"), 1, 0)
        g.addWidget(self.d_from, 1, 1)
        g.addWidget(QLabel("To"), 1, 2)
        g.addWidget(self.d_to, 1, 3)
        g.addWidget(btn_load, 2, 2)
        g.addWidget(btn_export, 2, 3)
        g.addWidget(btn_print, 2, 4)
        filt.setLayout(g)

        self.model = QSqlQueryModel(self)
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lbl_total = QLabel("Total Amount: ₹0.00")

        lay = QVBoxLayout(self)
        lay.addWidget(filt)
        lay.addWidget(self.view)
        lay.addWidget(self.lbl_total)

        btn_load.clicked.connect(self.load_data)
        btn_export.clicked.connect(self.export)
        btn_print.clicked.connect(self.print_invoice_simple)

    def reload_customers(self):
        self.cmb_farmer.clear()
        q = QSqlQuery("SELECT id, name FROM customers ORDER BY name ASC")
        while q.next():
            self.cmb_farmer.addItem(q.value(1), q.value(0))

    def load_data(self):
        cid = self.cmb_farmer.currentData()
        if cid is None:
            return
        d1 = self.d_from.date().toString('yyyy-MM-dd')
        d2 = self.d_to.date().toString('yyyy-MM-dd')
        sql = (
            "SELECT s.supply_date, s.crop, s.start_time, s.end_time, "
            "CAST(s.hours AS INTEGER) as h, CAST((s.hours - CAST(s.hours AS INTEGER)) * 60 AS INTEGER) as m, "
            "s.amount, s.notes "
            "FROM supplies s WHERE s.customer_id=? AND s.supply_date BETWEEN ? AND ? "
            "ORDER BY s.supply_date ASC, s.id ASC"
        )
        q = QSqlQuery()
        q.prepare(sql)
        q.addBindValue(cid)
        q.addBindValue(d1)
        q.addBindValue(d2)
        q.exec_()
        self.model.setQuery(q)
        headers = ["Date", "Crop", "Start", "Off", "Hours", "Minutes", "Amount", "Notes"]
        for i, h in enumerate(headers):
            self.model.setHeaderData(i, Qt.Horizontal, h)
        # total
        qsum = QSqlQuery("SELECT SUM(amount) FROM supplies WHERE customer_id=? AND supply_date BETWEEN ? AND ?")
        qsum.addBindValue(cid)
        qsum.addBindValue(d1)
        qsum.addBindValue(d2)
        qsum.exec_()
        total = 0.0
        if qsum.next():
            total = qsum.value(0) or 0.0
        self.lbl_total.setText(f"Total Amount: ₹{float(total):.2f}")
        
        # Update button states
        self.update_button_states()

    def export(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Invoice Data", f"invoice_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmm')}", "CSV (*.csv);;Excel (*.xlsx)")
        if not path:
            return
        headers = [self.model.headerData(i, Qt.Horizontal) for i in range(self.model.columnCount())]
        rows = []
        for r in range(self.model.rowCount()):
            rows.append([self.model.data(self.model.index(r, c)) for c in range(self.model.columnCount())])
        out = export_rows(headers, rows, path)
        QMessageBox.information(self, "Export", f"Exported to{out}")

    def invoice_html(self):
        """Generate HTML for invoice printing"""
        farmer = self.cmb_farmer.currentText()
        d1 = self.d_from.date().toString('yyyy-MM-dd')
        d2 = self.d_to.date().toString('yyyy-MM-dd')
        
        rows_html = ""
        total = 0.0
        
        # Check if we have data
        if self.model.rowCount() == 0:
            rows_html = """
                <tr>
                    <td colspan="8" style="text-align: center; padding: 20px; color: #666;">
                        No records found for the selected period
                    </td>
                </tr>
            """
        else:
            for r in range(self.model.rowCount()):
                vals = [self.model.data(self.model.index(r,c)) for c in range(self.model.columnCount())]
                if len(vals) >= 8:
                    dt, crop, st, et, hrs, mins, amt, notes = vals
                    
                    # Format data properly
                    dt_str = format_date_for_display(dt)
                    crop_str = safe_html_value(crop)
                    st_str = safe_html_value(st)
                    et_str = safe_html_value(et)
                    hrs_str = safe_html_value(hrs) if hrs is not None else "0"
                    mins_str = safe_html_value(mins) if mins is not None else "0"
                    amt_str = safe_html_value(amt) if amt else "0"
                    notes_str = safe_html_value(notes)
                    
                    # Calculate total
                    try:
                        total += float(amt or 0)
                    except (ValueError, TypeError):
                        pass
                    
                    rows_html += f"""
                        <tr>
                            <td>{dt_str}</td>
                            <td>{crop_str}</td>
                            <td>{st_str}</td>
                            <td>{et_str}</td>
                            <td>{hrs_str}</td>
                            <td>{mins_str}</td>
                            <td>{format_currency(float(amt or 0))}</td>
                            <td>{notes_str}</td>
                        </tr>
                    """
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Water Supply Invoice</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 12pt;
                    margin: 20px;
                    line-height: 1.4;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #333;
                    padding-bottom: 10px;
                }}
                .info {{
                    margin-bottom: 20px;
                }}
                .info div {{
                    margin: 5px 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    font-size: 10pt;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: center;
                    vertical-align: middle;
                }}
                th {{
                    background-color: #f0f0f0;
                    font-weight: bold;
                }}
                .amount {{
                    text-align: right;
                    font-weight: bold;
                }}
                .total-row {{
                    background-color: #f9f9f9;
                    font-weight: bold;
                }}
                .signature {{
                    margin-top: 40px;
                    text-align: right;
                }}
                @media print {{
                    body {{
                        margin: 10px;
                    }}
                    table {{
                        font-size: 9pt;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Water Supply Invoice</h2>
            </div>
            
            <div class="info">
                <div><strong>Farmer:</strong> {farmer}</div>
                <div><strong>Period:</strong> {d1} to {d2}</div>
                <div><strong>Rate:</strong> ₹{int(DEFAULT_RATE)}/hour</div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Crop</th>
                        <th>Start Time</th>
                        <th>End Time</th>
                        <th>Hours</th>
                        <th>Minutes</th>
                        <th>Amount</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
                <tfoot>
                    <tr class="total-row">
                        <td colspan="6"><strong>Total Amount</strong></td>
                        <td colspan="2" class="amount"><strong>{format_currency(total)}</strong></td>
                    </tr>
                </tfoot>
            </table>
            
            <div class="signature">
                <p>Signature: _________________</p>
                <p>Date: _________________</p>
            </div>
        </body>
        </html>
        """
        return html

    def print_invoice(self):
        """Print the invoice with preview"""
        if self.model.rowCount() == 0:
            QMessageBox.information(self, "Invoice", "No records to print")
            return
            
        try:
            printer = QPrinter(QPrinter.HighResolution)
            
            # Set print settings with fallback
            try:
                printer.setOrientation(QPrinter.Portrait)
            except AttributeError:
                # Fallback for older PyQt5 versions
                pass
                
            try:
                printer.setPageSize(QPrinter.A4)
            except AttributeError:
                # Fallback for older PyQt5 versions
                pass
                
            try:
                printer.setColorMode(QPrinter.GrayScale)
            except AttributeError:
                # Fallback for older PyQt5 versions
                pass
            
            preview = QPrintPreviewDialog(printer, self)
            preview.setWindowTitle("Print Preview — Invoice")
            preview.paintRequested.connect(self._render_preview)
            preview.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print invoice: {str(e)}")

    def _render_preview(self, printer):
        """Render the invoice for printing"""
        try:
            from PyQt5.QtGui import QTextDocument
            doc = QTextDocument()
            doc.setHtml(self.invoice_html())
            
            # Set document properties for better printing
            try:
                doc.setPageSize(printer.pageRect().size())
            except AttributeError:
                # Fallback for older PyQt5 versions
                pass
                
            doc.print_(printer)
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to render invoice: {str(e)}")

    def print_invoice_simple(self):
        """Simple print method for compatibility with all PyQt5 versions"""
        if self.model.rowCount() == 0:
            QMessageBox.information(self, "Invoice", "No records to print")
            return
            
        try:
            printer = QPrinter()
            printer.setResolution(300)  # High resolution
            
            preview = QPrintPreviewDialog(printer, self)
            preview.setWindowTitle("Print Preview — Invoice")
            preview.paintRequested.connect(self._render_preview_simple)
            preview.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to print invoice: {str(e)}")

    def _render_preview_simple(self, printer):
        """Simple render method for printing"""
        try:
            from PyQt5.QtGui import QTextDocument
            doc = QTextDocument()
            doc.setHtml(self.invoice_html())
            doc.print_(printer)
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Failed to render invoice: {str(e)}")

    def update_button_states(self):
        """Update button states based on data availability"""
        has_data = self.model.rowCount() > 0
        has_farmer = self.cmb_farmer.currentData() is not None
        
        # Find the print button in the layout
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QGroupBox):
                group_layout = widget.layout()
                if group_layout:
                    for j in range(group_layout.count()):
                        item = group_layout.itemAt(j)
                        if item and item.widget():
                            btn = item.widget()
                            if isinstance(btn, QPushButton) and "Print" in btn.text():
                                btn.setEnabled(has_data and has_farmer)
                                break

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self, on_logout=None):
        super().__init__()
        self.on_logout = on_logout
        self.setup_window()
        self.setup_tabs()
        self.setup_toolbar()
        self.load_settings()

    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle(f"{APP_NAME}")
        self.setMinimumSize(1100, 700)
        # Set the application icon
        try:
            self.setWindowIcon(QIcon("sewage-plant.png"))
        except Exception:
            # Fallback to theme icon if custom icon fails
            try:
                self.setWindowIcon(QIcon.fromTheme("applications-utilities"))
            except Exception:
                pass

    def setup_tabs(self):
        """Setup the tab widget"""
        self.tabs = QTabWidget()
        self.tab_customers = CustomersTab()
        self.tab_supply = SupplyTab()
        self.tab_reports = ReportsTab()
        self.tab_billing = BillingTab()
        
        self.tabs.addTab(self.tab_customers, "Customers")
        self.tabs.addTab(self.tab_supply, "Water Supply")
        self.tabs.addTab(self.tab_reports, "Reports")
        self.tabs.addTab(self.tab_billing, "Billing / Invoices")
        
        self.setCentralWidget(self.tabs)



    def setup_toolbar(self):
        """Setup the toolbar with all features"""
        tb = QToolBar("Main")
        tb.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, tb)

        # Create buttons with enhanced styling
        btn_about = QPushButton("About")
        btn_about.setToolTip("Show application information and features")
        
        btn_refresh = QPushButton("Reload Farmers")
        btn_refresh.setToolTip("Refresh farmer list in all tabs")
        
        btn_dark = QPushButton("Dark Mode")
        btn_dark.setCheckable(True)
        btn_dark.setToolTip("Toggle between dark and light themes")
        
        btn_time_format = QPushButton("12H Format")
        btn_time_format.setCheckable(True)
        btn_time_format.setToolTip("Toggle between 12-hour and 24-hour time format")
        
        btn_logout = QPushButton("Logout")
        btn_logout.setToolTip("Logout and return to login screen")

        # Connect signals
        btn_about.clicked.connect(self.show_about)
        btn_refresh.clicked.connect(self.reload_farmers_everywhere)
        btn_dark.toggled.connect(self.toggle_dark_mode)
        btn_time_format.toggled.connect(self.toggle_time_format)
        btn_logout.clicked.connect(self.do_logout)

        # Add to toolbar
        for btn in (btn_about, btn_refresh, btn_dark, btn_time_format, btn_logout):
            tb.addWidget(btn)
            
        # Store button references
        self.btn_dark = btn_dark
        self.btn_time_format = btn_time_format

    def toggle_time_format(self, enabled):
        """Toggle between 12-hour and 24-hour time format"""
        self.time_format_12h = enabled
        settings = QSettings("WaterSupplyApp", "Preferences")
        settings.setValue("timeformat12h", enabled)

        fmt = "hh:mm AP" if enabled else "HH:mm"
        self.tab_supply.t_start.setDisplayFormat(fmt)
        self.tab_supply.t_end.setDisplayFormat(fmt)
        self.tab_supply.auto_calc()

    def load_time_settings(self):
        """Load time format settings"""
        settings = QSettings("WaterSupplyApp", "Preferences")
        self.time_format_12h = settings.value("timeformat12h", False, type=bool)
        self.btn_time_format.setChecked(self.time_format_12h)
        fmt = "hh:mm AP" if self.time_format_12h else "HH:mm"
        self.tab_supply.t_start.setDisplayFormat(fmt)
        self.tab_supply.t_end.setDisplayFormat(fmt)

    def load_settings(self):
        """Load application settings"""
        settings = QSettings("WaterSupplyApp", "Preferences")
        if settings.value("darkmode", False, type=bool):
            self.btn_dark.setChecked(True)
        
        # Load time format settings
        self.load_time_settings()

    def toggle_dark_mode(self, enabled: bool):
        """Toggle dark mode"""
        settings = QSettings("WaterSupplyApp", "Preferences")
        settings.setValue("darkmode", enabled)
        QApplication.instance().setStyleSheet(dark_stylesheet if enabled else light_stylesheet)

    def reload_farmers_everywhere(self):
        """Reload farmers in all tabs"""
        try:
            self.tab_supply.reload_customers()
            self.tab_reports.reload_customers()
            self.tab_billing.reload_customers()
        except Exception as e:
            QMessageBox.warning(self, "Warning", f"Failed to reload farmers: {str(e)}")

    def do_logout(self):
        """Handle logout"""
        reply = QMessageBox.question(
            self, "Logout", "Do you want to logout?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes and self.on_logout:
            self.on_logout()

    def show_about(self):
        """Show about dialog"""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p><strong>Version:</strong> {VERSION}</p>
        <p><strong>Water Rate:</strong> ₹{int(DEFAULT_RATE)}/hour</p>
        <p><strong>Contact:</strong> {CONTACT}</p>
        <hr>
        """
        QMessageBox.information(self, "About", about_text)


# ---------- App Entry ----------
def run_app():
    """Main application entry point"""
    try:
        app = QApplication(sys.argv)
        
        # Load settings and apply theme
        settings = QSettings("WaterSupplyApp", "Preferences")
        if settings.value("darkmode", False, type=bool):
            app.setStyleSheet(dark_stylesheet)
        else:
            app.setStyleSheet(light_stylesheet)
        
        # Initialize database
        fresh = ensure_database()
        open_qt_db()

        def start_main():
            """Start the main application window"""
            def logout_then_show_login():
                main.close()
                show_login()

            nonlocal main
            main = MainWindow(on_logout=logout_then_show_login)
            main.show()
            
            if fresh:
                QMessageBox.information(
                    main, "Welcome", 
                    f"Default login created:\nUsername: admin\nPassword: admin"
                )

        def show_login():
            """Show login dialog"""
            dlg = LoginDialog()
            if dlg.exec_() == QDialog.Accepted:
                start_main()
            else:
                sys.exit(0)

        main = None
        show_login()
        sys.exit(app.exec_())
        
    except Exception as e:
        QMessageBox.critical(None, "Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()
