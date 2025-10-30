import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

mysql = MySQL(app)

@app.before_first_request
def create_tables():
    cur = mysql.connection.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        filepath VARCHAR(255) NOT NULL
    )
    """)
    mysql.connection.commit()
    cur.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs', methods=['GET'])
def get_songs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, filename, filepath FROM songs")
    songs = cur.fetchall()
    cur.close()
    return jsonify([{'id': song[0], 'filename': song[1], 'filepath': song[2]} for song in songs])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'files[]' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('files[]')
    
    for file in files:
        if file.filename == '':
            continue
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO songs (filename, filepath) VALUES (%s, %s)", (filename, filepath))
            mysql.connection.commit()
            cur.close()
            
    return jsonify({'message': 'Files uploaded successfully'})

@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT filepath FROM songs WHERE id = %s", [song_id])
    song = cur.fetchone()
    if song:
        filepath = song[0]
        if os.path.exists(filepath):
            os.remove(filepath)
        
        cur.execute("DELETE FROM songs WHERE id = %s", [song_id])
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Song deleted successfully'})
    cur.close()
    return jsonify({'error': 'Song not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
