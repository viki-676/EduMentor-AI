// EduMentor AI - Quiz Engine JS
document.addEventListener('DOMContentLoaded', function () {
    const quizForm = document.getElementById('quizForm');
    if (!quizForm) return;

    const timeTakenInput = document.getElementById('timeTakenInput');
    const timerDisplay = document.getElementById('timerDisplay');
    const progressText = document.getElementById('progressText');
    const progressBar = document.getElementById('progressBar');
    const durationMinutes = parseInt(quizForm.dataset.duration || '0', 10);

    let secondsElapsed = 0;
    let timerInterval = null;

    // Track total answering time
    timerInterval = setInterval(function () {
        secondsElapsed++;
        if (timeTakenInput) {
            timeTakenInput.value = secondsElapsed;
        }

        if (durationMinutes > 0 && timerDisplay) {
            const totalAllowedSeconds = durationMinutes * 60;
            const remaining = totalAllowedSeconds - secondsElapsed;

            if (remaining <= 0) {
                clearInterval(timerInterval);
                timerDisplay.textContent = "00:00 - Time's Up!";
                alert("Time has expired! Submitting your quiz now.");
                quizForm.submit();
            } else {
                const mins = Math.floor(remaining / 60);
                const secs = remaining % 60;
                timerDisplay.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
            }
        }
    }, 1000);

    // Update progress on option selection
    const radioInputs = document.querySelectorAll('.quiz-option-input');
    const totalQuestions = parseInt(quizForm.dataset.totalQuestions || '0', 10);

    function updateProgress() {
        const answeredQuestions = new Set();
        radioInputs.forEach(input => {
            if (input.checked) {
                answeredQuestions.add(input.name);
            }
        });

        const answeredCount = answeredQuestions.size;
        if (progressText) {
            progressText.textContent = `${answeredCount} of ${totalQuestions} answered`;
        }
        if (progressBar && totalQuestions > 0) {
            const pct = Math.round((answeredCount / totalQuestions) * 100);
            progressBar.style.width = `${pct}%`;
        }
    }

    radioInputs.forEach(input => {
        input.addEventListener('change', updateProgress);
    });

    updateProgress();

    // Confirm submission if questions remain unanswered
    quizForm.addEventListener('submit', function (e) {
        const answeredQuestions = new Set();
        radioInputs.forEach(input => {
            if (input.checked) {
                answeredQuestions.add(input.name);
            }
        });

        const answeredCount = answeredQuestions.size;
        if (answeredCount < totalQuestions) {
            const unanswered = totalQuestions - answeredCount;
            const proceed = confirm(`You have ${unanswered} unanswered question(s). Are you sure you want to submit?`);
            if (!proceed) {
                e.preventDefault();
                return;
            }
        }
        clearInterval(timerInterval);
    });
});
