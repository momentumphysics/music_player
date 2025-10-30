import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs', methods=['GET'])
def get_songs():
    songs = Song.query.all()
    return jsonify([{'id': song.id, 'filename': song.filename, 'filepath': song.filepath} for song in songs])

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
            
            new_song = Song(filename=filename, filepath=filepath)
            db.session.add(new_song)
            db.session.commit()
            
    return jsonify({'message': 'Files uploaded successfully'})

@app.route('/songs/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    song = Song.query.get(song_id)
    if song:
        if os.path.exists(song.filepath):
            os.remove(song.filepath)
        
        db.session.delete(song)
        db.session.commit()
        return jsonify({'message': 'Song deleted successfully'})
    return jsonify({'error': 'Song not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
