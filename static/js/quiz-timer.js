/**
 * SmartLearn — Quiz Countdown Timer & Auto-Submit Handler
 */

document.addEventListener('DOMContentLoaded', function () {
  const timerElement = document.getElementById('quizCountdown');
  const quizForm = document.getElementById('quizForm');

  if (!timerElement || !quizForm) return;

  let remainingSeconds = parseInt(timerElement.getAttribute('data-seconds'), 10);
  if (isNaN(remainingSeconds) || remainingSeconds <= 0) return;

  function updateTimerDisplay() {
    const minutes = Math.floor(remainingSeconds / 60);
    const seconds = remainingSeconds % 60;
    timerElement.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

    if (remainingSeconds <= 60) {
      timerElement.classList.add('text-danger', 'fw-bold');
    }

    if (remainingSeconds <= 0) {
      clearInterval(intervalId);
      timerElement.innerText = '00:00';
      alert('Time is up! Submitting your answers now.');
      quizForm.submit();
    }
    remainingSeconds--;
  }

  updateTimerDisplay();
  const intervalId = setInterval(updateTimerDisplay, 1000);
});
