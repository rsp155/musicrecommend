// static/app.js
document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("situation");
  const btn = document.getElementById("btn-recommend");
  const btnVoice = document.getElementById("btn-voice");
  const voiceStatus = document.getElementById("voice-status");
  const resultsBox = document.getElementById("results");

  function esc(s) {
    return String(s ?? "").replace(/[&<>"']/g, m => ({
      "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"
    }[m]));
  }
  function chip(label, value) {
    if (!value) return "";
    return `<span class="chip"><b>${esc(label)}:</b> ${esc(value)}</span>`;
  }

  function render(results, tags) {
    const tagRow = `
      <div class="tags-row">
        ${chip("장르", tags.genre)}
        ${chip("무드", tags.mood)}
        ${chip("에너지", tags.energy)}
        ${chip("템포", tags.tempo)}
        ${chip("언어", tags.language)}
      </div>
    `;

    if (!Array.isArray(results) || results.length === 0) {
      resultsBox.innerHTML = `${tagRow}<div class="empty">조건에 맞는 곡을 찾지 못했습니다.</div>`;
      return;
    }

    const cards = results.map(r => {
      const title = esc(r.title);
      const artist = esc(r.artist);
      const genre = esc(r.genre || "");
      const mood = esc(r.mood || "");
      const energy = esc(r.energy || "");
      const tempo = esc(r.tempo || "");
      const lang = esc(r.language || "");

      const links = r.links || {};
      const yt = links.youtube ? `<a class="btn btn-xs" target="_blank" href="${esc(links.youtube)}">YouTube</a>` : "";
      const ytm = links.ytmusic ? `<a class="btn btn-xs" target="_blank" href="${esc(links.ytmusic)}">YT Music</a>` : "";
      const sp = links.spotify ? `<a class="btn btn-xs" target="_blank" href="${esc(links.spotify)}">Spotify</a>` : "";

      return `
        <div class="card">
          <div class="title">${title}</div>
          <div class="artist">${artist}</div>
          <div class="meta">
            ${chip("장르", genre)} ${chip("무드", mood)} ${chip("에너지", energy)}
            ${chip("템포", tempo)} ${chip("언어", lang)}
          </div>
          <div class="links">${yt} ${ytm} ${sp}</div>
        </div>
      `;
    }).join("");

    resultsBox.innerHTML = `${tagRow}${cards}`;
  }

  async function ask(text) {
    resultsBox.innerHTML = `<div class="loading">추천을 불러오는 중...</div>`;
    try {
      const res = await fetch("/api/recommend", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ content: text })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      const results = data?.results ?? [];
      const tags = data?.tags ?? {};
      render(results, tags);
    } catch (err) {
      console.error(err);
      resultsBox.innerHTML = `<div class="error">서버 오류: ${esc(err.message)}</div>`;
    }
  }

  // ===== 음성 인식(Web Speech API) =====
  let recognition = null;
  let recActive = false;

  function supportSpeech() {
    return ("webkitSpeechRecognition" in window) || ("SpeechRecognition" in window);
  }

  function createRecognizer() {
    const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
    const rec = new Rec();
    rec.lang = "ko-KR";          // 한국어
    rec.interimResults = true;   // 중간결과 표시
    rec.maxAlternatives = 1;
    rec.continuous = false;      // 한 문장 끝나면 자동 종료
    return rec;
  }

  function startVoice() {
    if (!supportSpeech()) {
      voiceStatus.textContent = "이 브라우저는 음성인식을 지원하지 않습니다.";
      return;
    }
    if (recActive) return;

    recognition = createRecognizer();
    recActive = true;
    btnVoice.textContent = "⏹️ 종료";
    voiceStatus.textContent = "듣는 중... 말한 뒤 잠시 기다리세요.";

    let finalText = "";
    recognition.onresult = (e) => {
      let interim = "";
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const tr = e.results[i][0].transcript;
        if (e.results[i].isFinal) {
          finalText += tr;
        } else {
          interim += tr;
        }
      }
      textarea.value = (finalText + (interim ? " " + interim : "")).trim();
    };

    recognition.onerror = (e) => {
      console.error("speech error:", e);
      voiceStatus.textContent = `음성 오류: ${e.error || "unknown"}`;
    };

    recognition.onend = () => {
      // 종료 시 자동 추천 호출(최종 텍스트가 있으면)
      recActive = false;
      btnVoice.textContent = "🎙️ 음성 입력";
      if (textarea.value.trim()) {
        voiceStatus.textContent = "인식 완료. 추천 가져오는 중…";
        ask(textarea.value.trim());
      } else {
        voiceStatus.textContent = "아무 말도 인식되지 않았어요.";
      }
    };

    recognition.start();
  }

  function stopVoice() {
    if (recognition && recActive) {
      recognition.stop();
    }
  }

  btnVoice?.addEventListener("click", () => {
    if (!recActive) startVoice();
    else stopVoice();
  });

  // ===== 추천 버튼 =====
  btn?.addEventListener("click", () => {
    const text = (textarea?.value || "").trim();
    if (!text) {
      resultsBox.innerHTML = `<div class="empty">상황/분위기를 입력해 주세요.</div>`;
      return;
    }
    ask(text);
  });
});
