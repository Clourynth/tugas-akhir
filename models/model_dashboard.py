import MySQLdb.cursors
from datetime import datetime

class DashboardModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_statistics(self):
        """Get detection statistics"""
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Total bridges
        cursor.execute('SELECT COUNT(*) as total FROM jembatan')
        total = cursor.fetchone()['total']
        
        # Bridges with cracks
        cursor.execute('SELECT COUNT(*) as with_cracks FROM jembatan WHERE detected = TRUE')
        with_cracks = cursor.fetchone()['with_cracks']
        
        # Bridges without cracks
        cursor.execute('SELECT COUNT(*) as without_cracks FROM jembatan WHERE detected = FALSE')
        without_cracks = cursor.fetchone()['without_cracks']
        
        cursor.close()
        
        return {
            'total': total,
            'with_cracks': with_cracks,
            'without_cracks': without_cracks
        }
        """Save bridge detection result to database"""
        cursor = self.mysql.connection.cursor()
        
        confidence_scores = ','.join([str(pred['score']) for pred in data.get('predictions', [])])
        
        cursor.execute('''
            INSERT INTO jembatan (
                nama_jembatan, lokasi, original_image_path, annotated_image_path,
                detected, num_detections, confidence_scores, user_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['nama_jembatan'],
            data['lokasi'],
            data['original_image_path'],
            data['annotated_image_path'],
            data['detected'],
            data['num_detections'],
            confidence_scores,
            data['user_id']
        ))
        
        self.mysql.connection.commit()
        jembatan_id = cursor.lastrowid
        cursor.close()
        return jembatan_id

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

    def delete_jembatan(self, jembatan_id):
        """Delete bridge record"""
        cursor = self.mysql.connection.cursor()
        cursor.execute('DELETE FROM jembatan WHERE id = %s', (jembatan_id,))
        self.mysql.connection.commit()
        cursor.close()
        return cursor.rowcount > 0

    def get_statistics(self):
        """Get detection statistics"""
        cursor = self.mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Total bridges
        cursor.execute('SELECT COUNT(*) as total FROM jembatan')
        total = cursor.fetchone()['total']
        
        # Bridges with cracks
        cursor.execute('SELECT COUNT(*) as with_cracks FROM jembatan WHERE detected = TRUE')
        with_cracks = cursor.fetchone()['with_cracks']
        
        # Bridges without cracks
        cursor.execute('SELECT COUNT(*) as without_cracks FROM jembatan WHERE detected = FALSE')
        without_cracks = cursor.fetchone()['without_cracks']
        
        cursor.close()
        
        return {
            'total': total,
            'with_cracks': with_cracks,
            'without_cracks': without_cracks
        }
