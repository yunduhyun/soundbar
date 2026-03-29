document.addEventListener('DOMContentLoaded', function () {
  //웹 페이지의 모든 글자와 상자가 화면에 나타난 직후 아래 함수를 실행
  const bgContainer = document.querySelector('.background-image');
  const inputFields = document.querySelectorAll('.input-id, .input-pw');

  if (bgContainer) {
    inputFields.forEach((input) => {
      input.addEventListener('focus', () => {
        bgContainer.classList.add('shaking-bg', 'falling-scream');
        input.classList.add('shaking-input');
      });
      input.addEventListener('blur', () => {
        bgContainer.classList.remove('shaking-bg', 'falling-scream');
        input.classList.remove('shaking-input');
      });
    });
  }

  //<--------------------------페이지 진동 기능 ⬆️------------------------->

  //<----------------------비커 및 input의 range 조절 ⬇️------------------>
  const screamBtn = document.getElementById('scream-btn');
  const liquid = document.getElementById('liquid');
  const dbText = document.getElementById('dB-value');
  //Tag의 ID를 이용해서 변수를 지정함

  let mediaRecorder;
  let audioChunks = [];
  let audioContext;
  let analyser;
  let maxDecibel;

  if (screamBtn) {
    screamBtn.addEventListener('click', async () => {
      if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
        screamBtn.innerText = '소리 조절 시작 !';
        return;
      }

      try {
        maxDecibel = 0;
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });

        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];
        mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
          sendScreamToServer(audioBlob, maxDecibel);
        };

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(stream);
        // 2. 연결 순서: 마이크 -> 분석기 -> 볼륨조절기 -> 스피커(출력)
        source.connect(analyser);
        analyser.fftSize = 256;
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        function updateBeaker() {
          const volumSlider = document.querySelector('input[type="range"]');
          // analyser가 없거나 녹음 중이 아니면 중단
          if (
            !analyser ||
            !mediaRecorder ||
            mediaRecorder.state !== 'recording'
          )
            return;

          analyser.getByteFrequencyData(dataArray);
          let sum = 0;
          dataArray.forEach((v) => (sum += v));
          let average = sum / dataArray.length;

          if (average > maxDecibel) {
            maxDecibel = Math.floor(average);
          }
          // 비커 수위 계산 (0.5 감도)
          const level = Math.min(average * 0.5, 100);
          if (liquid) liquid.style.height = level + '%';
          if (volumSlider) {
            volumSlider.value = level;
          }
          if (dbText) dbText.innerText = Math.floor(average) + 'dB';

          // 다음 프레임 예약
          requestAnimationFrame(updateBeaker);
        }

        mediaRecorder.start();
        updateBeaker();

        screamBtn.innerText = '비명 중단 및 저장';
      } catch (err) {
        console.error(err);
        alert('마이크 권한이 필요합니다잉!');
      }
    });
  }
});

//<--------------------------비커 및 input의 range 조절 ⬆️----------------------->

// <----------------------------- 파일 저장 ⬇️ --------------------------------->

function sendScreamToServer(blob, maxdB) {
  const formData = new FormData();
  formData.append('sound_file', blob, 'sound.wav');
  formData.append('decibel', maxdB);

  fetch('/upload_sound', { method: 'POST', body: formData })
    .then((res) => res.json())
    .then((data) => alert('저장 완료! 최고 데시벨🔥: ' + maxdB + 'dB'))
    .catch((err) => console.error('저장 실패:', err));
}

//<----------------------------- 파일 저장 ⬆️ ---------------------------------->

//<-------------------------------파일 삭제 ⬇️---------------------------------->

function deleteSound(filename, cardId) {
  if (!confirm('정말 삭제 하시겠습니까 ?')) return;

  fetch('/delete_sound', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename: filename }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === 'success') {
        const card = document.getElementById(cardId);
        card.style.transition = 'all 0.5s';
        card.style.opacity = '0';
        card.style.transform = 'translateX(100px)';
        setTimeout(() => card.remove(), 500);
      } else {
        alert('삭제 실패: ' + data.message);
      }
    })
    .catch((err) => console.error('에러 발생:', err));
}

//<-----------------------------파일 삭제⬆️ ------------------------------------>

//<--------------------------메인.js에 묶기 위한 노력 ⬇️--------------------------->
const bgContainer = document.querySelector('.background-image');
const inputFields = document.querySelectorAll(
  '.input-id, .input-pw, .input-nickname',
);

if (bgContainer) {
  inputFields.forEach((input) => {
    input.addEventListener('focus', () => {
      bgContainer.classList.add('shaking-bg');
      input.classList.add('shaking-input');
    });
    input.addEventListener('blur', () => {
      bgContainer.classList.remove('shaking-bg');
      input.classList.remove('shaking-input');
    });
    input.addEventListener('input', () => {
      input.classList.add('bouncing-input');

      setTimeout(() => {
        input.classList.remove('bouncing-input');
      }, 100);
    });
  });
}
