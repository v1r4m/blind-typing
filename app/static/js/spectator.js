const socket = io();
let currentSentence = '';
let isAdmin = false;

document.addEventListener('DOMContentLoaded', () => {
    const nickname = sessionStorage.getItem('nickname');
    const role = sessionStorage.getItem('role');

    if (!nickname || (role !== 'spectator' && role !== 'admin')) {
        window.location.href = '/';
        return;
    }

    isAdmin = role === 'admin';
    document.getElementById('my-nickname').textContent = nickname;
    document.getElementById('role-badge').textContent = isAdmin ? '[어드민]' : '[관전자]';

    if (isAdmin) {
        document.getElementById('admin-controls').classList.remove('hidden');
    }

    socket.emit('join_game', { nickname, role });
});

socket.on('room_update', (data) => {
    updateUI(data);
});

socket.on('joined', (data) => {
    if (data.room_info) {
        updateUI(data.room_info);
    }
});

socket.on('game_started', (data) => {
    currentSentence = data.sentence;
    document.getElementById('sentence-display').classList.remove('hidden');
    document.getElementById('current-sentence').textContent = currentSentence;
    document.getElementById('game-state').textContent = '진행 중';
    document.getElementById('game-state').className = 'status-badge playing';
    document.getElementById('winner-banner').classList.add('hidden');

    updateUI(data.room_info);
});

socket.on('typing_broadcast', (data) => {
    renderPlayers(data.players);
});

socket.on('game_over', (data) => {
    document.getElementById('game-state').textContent = '게임 종료';
    document.getElementById('game-state').className = 'status-badge finished';

    document.getElementById('winner-banner').classList.remove('hidden');
    document.getElementById('winner-name').textContent = data.winner;
    document.getElementById('winner-time').textContent = data.finish_time.toFixed(2);

    updateUI(data.room_info);
});

socket.on('game_reset', (data) => {
    currentSentence = '';
    document.getElementById('sentence-display').classList.add('hidden');
    document.getElementById('game-state').textContent = '대기 중';
    document.getElementById('game-state').className = 'status-badge waiting';
    document.getElementById('winner-banner').classList.add('hidden');

    updateUI(data.room_info);
});

socket.on('error', (data) => {
    alert(data.message);
});

function startGame() {
    const language = document.getElementById('language-select').value;
    socket.emit('start_game', { language });
}

function resetGame() {
    socket.emit('reset_game');
}

function updateUI(roomInfo) {
    renderPlayers(roomInfo.players);
}

function renderPlayers(players) {
    const grid = document.getElementById('players-grid');

    if (players.length === 0) {
        grid.innerHTML = '<p class="no-players">아직 플레이어가 없습니다.</p>';
        return;
    }

    grid.innerHTML = players.map(player => {
        const progress = currentSentence
            ? (player.current_input.length / currentSentence.length * 100).toFixed(0)
            : 0;

        return `
            <div class="player-card ${player.is_finished ? 'finished' : ''}">
                <div class="player-header">
                    <h3>${player.nickname}</h3>
                    ${player.is_finished ? '<span class="finished-badge">완료!</span>' : ''}
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: ${Math.min(progress, 100)}%"></div>
                </div>
                <p class="progress-text">${Math.min(progress, 100)}%</p>
                <div class="typing-display">
                    ${renderTypingWithErrors(player.current_input, player.errors)}
                </div>
                <div class="error-count">
                    실수: <span class="error-number">${player.errors.length}</span>개
                </div>
            </div>
        `;
    }).join('');
}

function renderTypingWithErrors(input, errors) {
    if (!input) return '<span class="placeholder">입력 대기 중...</span>';

    const errorPositions = new Set(errors.map(e => e.position));
    let html = '';

    for (let i = 0; i < input.length; i++) {
        const char = input[i];
        const isError = errorPositions.has(i);
        const errorInfo = errors.find(e => e.position === i);

        if (isError) {
            html += `<span class="error-char" title="예상: '${errorInfo.expected}'">${char}</span>`;
        } else {
            html += `<span class="correct-char">${char}</span>`;
        }
    }

    return html;
}
