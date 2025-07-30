import MySQLdb.cursors
from datetime import datetime

class DetectionModel:
    def __init__(self, mysql):
        self.mysql = mysql

    def create_table(self):
        """Create jembatan table if it doesn't exist"""
        cursor = self.mysql.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jembatan (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama_jembatan VARCHAR(255) NOT NULL,
                lokasi VARCHAR(255) NOT NULL,
                original_image_path VARCHAR(500),
                annotated_image_path VARCHAR(500),
                detected BOOLEAN DEFAULT FALSE,
                num_detections INT DEFAULT 0,
                confidence_scores TEXT,
                user_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        self.mysql.connection.commit()
        cursor.close()

    def save_detection_result(self, data):
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
