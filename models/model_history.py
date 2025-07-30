import MySQLdb.cursors

class HistoryModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_all_jembatan(self, user_id=None):
        """Get all bridge records, optionally filtered by user"""
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        if user_id:
            cursor.execute('''
                SELECT j.*, u.username 
                FROM jembatan j 
                LEFT JOIN users u ON j.user_id = u.id 
                WHERE j.user_id = %s 
                ORDER BY j.created_at DESC
            ''', (user_id,))
        else:
            cursor.execute('''
                SELECT j.*, u.username 
                FROM jembatan j 
                LEFT JOIN users u ON j.user_id = u.id 
                ORDER BY j.created_at DESC
            ''')
        
        jembatan_list = cursor.fetchall()
        cursor.close()
        return jembatan_list

    def delete_jembatan(self, jembatan_id):
        """Delete bridge record"""
        cursor = self.mysql.connection.cursor()
        cursor.execute('DELETE FROM jembatan WHERE id = %s', (jembatan_id,))
        self.mysql.connection.commit()
        cursor.close()
        return cursor.rowcount > 0

    def get_jembatan_by_id(self, jembatan_id):
        """Get specific bridge record by ID"""
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            SELECT j.*, u.username 
            FROM jembatan j 
            LEFT JOIN users u ON j.user_id = u.id 
            WHERE j.id = %s
        ''', (jembatan_id,))
        
        jembatan = cursor.fetchone()
        cursor.close()
        return jembatan
