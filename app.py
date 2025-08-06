from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import os
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
from pprint import pformat
from functools import wraps
from utils.predictor import CrackDetector

from models.model_login import UserModel
from models.model_dashboard import DashboardModel
from models.model_detection import DetectionModel
from models.model_history import HistoryModel

app = Flask(__name__)
app.secret_key = "secret_key"  # Tambahkan secret key untuk session

# Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # sesuaikan dengan password mysql kamu
app.config['MYSQL_DB'] = 'db_deteksiretakan'

mysql = MySQL(app)
# Inisialisasi user_model agar bisa digunakan
user_model = UserModel(mysql)
dashboard_model = DashboardModel(mysql)
detection_model = DetectionModel(mysql)
history_model = HistoryModel(mysql)

# Create tables on startup
with app.app_context():
    try:
        detection_model.create_table()
    except Exception as e:
        print(f"Error creating tables: {e}")

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin") or session.get("role") != "admin":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("loggedin") or session.get("role") != "user":
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# @app.route('/debug-users')
# def debug_users():
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute("SELECT * FROM users")
#     users = cursor.fetchall()
    
#     # Debug print (seperti var_dump)
#     from pprint import pprint
#     pprint(users)

#     return f"<pre>{users}</pre>"  # tampilkan di browser (raw output)
@app.route('/debug-session')
def debug_users():
    users = session
    
  # Format isi session sebagai teks
    session_data = pformat(dict(session))
    
    # Tampilkan ke browser dalam <pre> agar rapi
    return f"<pre>{session_data}</pre>"

@app.route("/login", methods=["GET", "POST"])
def login():
    # Jika sudah login, redirect sesuai role
    if session.get('loggedin'):
        if session.get('role') == 'admin':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('detection'))

    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        user = user_model.find_by_username(username)

        if user_model.validate_password(user, password):
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            session['role'] = user.get('role', 'user')
            if session['role'] == 'admin':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('detection'))
        else:
            message = 'Username atau password salah!'
    return render_template('login.html', message=message)

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Hapus semua data session
    return redirect(url_for('login'))  # Kembali ke halaman login


@app.route("/dashboard", methods=["GET", "POST"])
@admin_required
def dashboard():
    username = session['username']
    
    # Get statistics
    stats = dashboard_model.get_statistics()
    
    # Get all bridge data for admin
    jembatan_list = history_model.get_all_jembatan()
    
    return render_template("admin/dashboard.html", user=username, stats=stats, jembatan_list=jembatan_list)

# Konfigurasi folder upload
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Inisialisasi detector
detector = CrackDetector()

@app.route("/detection", methods=["GET", "POST"])
@user_required
def detection():
    username = session['username']
    user_id = session['id']

    result = None  # Initialize result variable
    
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('No file uploaded', 'error')
            return render_template("user/detection.html", result=result)
            
        file = request.files['image']
        if file.filename == '':
            flash('No selected file', 'error')
            return render_template("user/detection.html", result=result)
            
        if file:
            # Get form data
            nama_jembatan = request.form.get('nama_jembatan', '')
            lokasi = request.form.get('lokasi', '')
            
            # Simpan file yang diupload
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Lakukan prediksi menggunakan detector
            prediction_result = detector.predict(filepath, save_annotated=True, output_dir=app.config['UPLOAD_FOLDER'])
            
            # Format result untuk template
            result = {
                'detected': prediction_result['detected'],
                'original_image_path': f'uploads/{filename}',
                'annotated_image_path': prediction_result['annotated_image_path'],
                'num_detections': prediction_result['num_detections'],
                'predictions': prediction_result['predictions'],
                'nama_jembatan': nama_jembatan,
                'lokasi': lokasi,
                'user_id': user_id
            }
            
            # Save to database
            try:
                jembatan_id = detection_model.save_detection_result(result)
                result['id'] = jembatan_id
                
                if prediction_result['detected']:
                    flash(f'Retakan terdeteksi! Ditemukan {prediction_result["num_detections"]} area retakan. Data telah disimpan.', 'success')
                else:
                    flash('Tidak ada retakan yang terdeteksi. Data telah disimpan.', 'info')
            except Exception as e:
                flash(f'Error menyimpan data: {str(e)}', 'error')

    return render_template("user/detection.html", result=result, user=username)

@app.route("/history")
@user_required
def history():
    """Show user's detection history"""
    username = session['username']
    user_id = session['id']
    
    jembatan_list = history_model.get_all_jembatan(user_id)
    
    return render_template("user/history.html", user=username, jembatan_list=jembatan_list)

@app.route("/delete_jembatan/<int:jembatan_id>", methods=["POST"])
@admin_required
def delete_jembatan(jembatan_id):
    """Delete bridge record (admin only)"""
    try:
        # Get image paths before deletion for cleanup
        jembatan = history_model.get_jembatan_by_id(jembatan_id)
        
        if history_model.delete_jembatan(jembatan_id):
            # Optional: Delete image files
            if jembatan:
                try:
                    if jembatan['original_image_path']:
                        os.remove(os.path.join('static', jembatan['original_image_path']))
                    if jembatan['annotated_image_path']:
                        os.remove(os.path.join('static', jembatan['annotated_image_path']))
                except:
                    pass  # Ignore file deletion errors
            
            flash('Data jembatan berhasil dihapus', 'success')
        else:
            flash('Gagal menghapus data jembatan', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('dashboard'))

@app.route("/delete_user_jembatan/<int:jembatan_id>", methods=["POST"])
@user_required
def delete_user_jembatan(jembatan_id):
    """Delete bridge record (user can only delete their own data)"""
    try:
        user_id = session['id']
        
        # Get jembatan data to verify ownership
        jembatan = history_model.get_jembatan_by_id(jembatan_id)
        
        if not jembatan:
            flash('Data tidak ditemukan', 'error')
            return redirect(url_for('history'))
        
        # Check if user owns this data
        if jembatan['user_id'] != user_id:
            flash('Anda tidak memiliki izin untuk menghapus data ini', 'error')
            return redirect(url_for('history'))
        
        if history_model.delete_jembatan(jembatan_id):
            # Optional: Delete image files
            try:
                if jembatan['original_image_path']:
                    os.remove(os.path.join('static', jembatan['original_image_path']))
                if jembatan['annotated_image_path']:
                    os.remove(os.path.join('static', jembatan['annotated_image_path']))
            except:
                pass  # Ignore file deletion errors
            
            flash('Data berhasil dihapus', 'success')
        else:
            flash('Gagal menghapus data', 'error')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    
    return redirect(url_for('history'))

if __name__ == "__main__":
    app.run(debug=True)
