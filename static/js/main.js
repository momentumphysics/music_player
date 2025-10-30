document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const playlist = document.getElementById('playlist');
    const audioPlayer = document.getElementById('audio-player');
    const songTitle = document.getElementById('song-title');
    const songArtist = document.getElementById('song-artist');
    const songArt = document.getElementById('song-art');
    const artPlaceholder = document.getElementById('art-placeholder');

    let currentSongId = null;

    const fetchSongs = async () => {
        try {
            const response = await fetch('/songs');
            const songs = await response.json();
            renderPlaylist(songs);
        } catch (error) {
            console.error('Error fetching songs:', error);
        }
    };

    const renderPlaylist = (songs) => {
        playlist.innerHTML = '';
        songs.forEach(song => {
            const li = document.createElement('li');
            li.dataset.id = song.id;
            li.dataset.filepath = song.filepath;
            li.classList.toggle('active', song.id === currentSongId);

            const songInfo = document.createElement('div');
            songInfo.className = 'song-info';
            songInfo.textContent = song.filename.replace(/\.mp3|\.wav|\.ogg|\.flac/gi, '');
            li.appendChild(songInfo);

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.innerHTML = '<span class="material-symbols-outlined">delete</span>';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                deleteSong(song.id);
            });
            li.appendChild(deleteBtn);

            li.addEventListener('click', () => {
                playSong(song.filepath, song.filename, song.id);
            });

            playlist.appendChild(li);
        });
    };

    const playSong = (filepath, filename, songId) => {
        audioPlayer.src = filepath;
        audioPlayer.play();
        songTitle.textContent = filename.replace(/\.mp3|\.wav|\.ogg|\.flac/gi, '');
        songArtist.textContent = 'Unknown Artist'; 
        
        document.querySelectorAll('#playlist li').forEach(item => {
            item.classList.remove('active');
        });
        const currentPlaylistItem = document.querySelector(`#playlist li[data-id='${songId}']`);
        if(currentPlaylistItem) {
            currentPlaylistItem.classList.add('active');
        }

        currentSongId = songId;
        songArt.style.display = 'none';
        artPlaceholder.style.display = 'flex';
    };

    const deleteSong = async (songId) => {
        try {
            const response = await fetch(`/songs/${songId}`, { method: 'DELETE' });
            if (response.ok) {
                if (currentSongId === songId) {
                    audioPlayer.pause();
                    audioPlayer.src = '';
                    songTitle.textContent = 'Select a song to play';
                    songArtist.textContent = 'No artist';
                    currentSongId = null;
                }
                fetchSongs();
            } else {
                console.error('Failed to delete song');
            }
        } catch (error) {
            console.error('Error deleting song:', error);
        }
    };

    const uploadFiles = async (files) => {
        const formData = new FormData();
        for (const file of files) {
            formData.append('files[]', file);
        }

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                fetchSongs();
            } else {
                console.error('File upload failed');
            }
        } catch (error) {
            console.error('Error uploading files:', error);
        }
    };

    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            uploadFiles(fileInput.files);
        }
    });

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            uploadFiles(e.dataTransfer.files);
        }
    });

    fetchSongs();
});
