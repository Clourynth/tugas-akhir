from werkzeug.security import check_password_hash
from flask_mysqldb import MySQL
import MySQLdb.cursors

class UserModel:
    def __init__(self, db):
        self.db = db

    def find_by_username(self, username):
        cursor = self.db.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()

    def validate_password(self, user, password_input):
        if user:
            return check_password_hash(user['password'], password_input)
        return False