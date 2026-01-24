#!/usr/bin/env python3
"""
Password reset script for the Tasks app.

Usage:
    python reset_password.py <username>
"""
import sys
import os
import getpass
import bcrypt
from mysql.connector import connect


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def reset_password(user_name):
    db_args = {
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASS'),
        'host': os.getenv('MYSQL_HOST'),
        'database': os.getenv('MYSQL_TASKS_DB'),
    }

    conn = connect(**db_args)
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT user_name FROM users WHERE user_name = %s", (user_name,))
    if not cursor.fetchone():
        print(f"Error: User '{user_name}' not found.")
        conn.close()
        return False

    # Get new password
    password = getpass.getpass("Enter new password (min 8 chars): ")
    if len(password) < 8:
        print("Error: Password must be at least 8 characters.")
        conn.close()
        return False

    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Error: Passwords do not match.")
        conn.close()
        return False

    # Update password
    password_hash = hash_password(password)
    cursor.execute(
        "UPDATE users SET password_hash = %s, updated_at = NOW() WHERE user_name = %s",
        (password_hash, user_name)
    )
    conn.commit()
    conn.close()

    print(f"Password reset successfully for user '{user_name}'.")
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python reset_password.py <username>")
        sys.exit(1)

    user_name = sys.argv[1]
    success = reset_password(user_name)
    sys.exit(0 if success else 1)
