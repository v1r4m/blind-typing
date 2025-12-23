const socket = io();
let currentSentence = '';

document.addEventListener('DOMContentLoaded', () => {
    const nickname = sessionStorage.getItem('nickname');
    const role = sessionStorage.getItem('role');

    if (!nickname || role !== 'player') {
        window.location.href = '/';
        return;
    }

    document.getElementById('my-nickname').textContent = nickname;

    socket.emit('join_game', { nickname, role: 'player' });
});

socket.on('room_update', (data) => {
    updatePlayerList(data.players);
});

socket.on('joined', (data) => {
    if (data.room_info) {
        updatePlayerList(data.room_info.players);
    }
});

socket.on('game_started', (data) => {
    currentSentence = data.sentence;

    document.getElementById('waiting-room').classList.add('hidden');
    document.getElementById('result-area').classList.add('hidden');
    document.getElementById('game-area').classList.remove('hidden');

    document.getElementById('target-sentence').textContent = currentSentence;

    const input = document.getElementById('typing-input');
    input.value = '';
    input.focus();
});

socket.on('typing_broadcast', (data) => {
    const myNickname = sessionStorage.getItem('nickname');
    const myPlayer = data.players.find(p => p.nickname === myNickname);

    if (myPlayer) {
        const progress = (myPlayer.current_input.length / currentSentence.length * 100).toFixed(0);
        document.getElementById('my-progress').style.width = `${Math.min(progress, 100)}%`;
        document.getElementById('progress-text').textContent = Math.min(progress, 100);
    }
});

socket.on('game_over', (data) => {
    document.getElementById('game-area').classList.add('hidden');
    document.getElementById('result-area').classList.remove('hidden');

    const myNickname = sessionStorage.getItem('nickname');
    const isWinner = data.winner === myNickname;

    document.getElementById('result-title').textContent = isWinner ? '🎉 승리!' : '게임 종료';
    document.getElementById('result-message').textContent = isWinner
        ? `${data.finish_time.toFixed(2)}초 만에 완료!`
        : `${data.winner}님이 승리했습니다!`;
});

socket.on('game_reset', (data) => {
    document.getElementById('game-area').classList.add('hidden');
    document.getElementById('result-area').classList.add('hidden');
    document.getElementById('waiting-room').classList.remove('hidden');

    document.getElementById('typing-input').value = '';
    updatePlayerList(data.room_info.players);
});

socket.on('error', (data) => {
    alert(data.message);
});

document.getElementById('typing-input').addEventListener('input', (e) => {
    socket.emit('typing_update', { text: e.target.value });
});

function updatePlayerList(players) {
    const list = document.getElementById('player-list');
    list.innerHTML = players.map(p =>
        `<li>${p.nickname} ${p.is_finished ? '✅' : ''}</li>`
    ).join('');
}
