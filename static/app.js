const promptInput = document.getElementById('prompt');
const recommendBtn = document.getElementById('recommend-btn');
const resultsList = document.getElementById('results-list');

function renderTracks(tracks) {
  resultsList.innerHTML = '';
  if (!tracks || tracks.length === 0) {
    resultsList.innerHTML = '<li>추천 결과가 없습니다.</li>';
    return;
  }
  for (const t of tracks) {
    const li = document.createElement('li');
    li.className = 'card';
    li.innerHTML = `
      <div class="title">${t.title}</div>
      <div class="meta">${t.artist} · ${t.genre || ''} · ${t.mood || ''}</div>
      <div class="reason">${t.reason || ''}</div>
    `;
    resultsList.appendChild(li);
  }
}

recommendBtn.addEventListener('click', async () => {
  const content = promptInput.value.trim();
  if (!content) {
    alert('내용을 입력해주세요.');
    return;
  }

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ input_type: 'text', content })
    });
    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }
    renderTracks(data.tracks);
  } catch (e) {
    console.error(e);
    alert('요청 중 오류가 발생했습니다.');
  }
});
