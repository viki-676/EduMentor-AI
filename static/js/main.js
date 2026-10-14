// EduMentor AI - Main JS Utility & Accessible Form Controls
document.addEventListener('DOMContentLoaded', function () {
    // 1. Auto-dismiss flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // 2. Global Accessible Password Show / Hide Toggle
    const passwordToggles = document.querySelectorAll('.toggle-password-btn');
    passwordToggles.forEach(function (button) {
        button.addEventListener('click', function () {
            const targetId = this.dataset.target;
            const input = targetId ? document.getElementById(targetId) : this.closest('.input-group').querySelector('input');
            const icon = this.querySelector('i');

            if (input) {
                if (input.type === 'password') {
                    input.type = 'text';
                    if (icon) {
                        icon.classList.remove('bi-eye');
                        icon.classList.add('bi-eye-slash');
                    }
                    this.setAttribute('aria-label', 'Hide password');
                } else {
                    input.type = 'password';
                    if (icon) {
                        icon.classList.remove('bi-eye-slash');
                        icon.classList.add('bi-eye');
                    }
                    this.setAttribute('aria-label', 'Show password');
                }
            }
        });
    });

    // 3. Quiz Configuration Modal Dynamic Controller
    const quizModalEl = document.getElementById('quizConfigModal');
    if (quizModalEl) {
        const pathInput = document.getElementById('configPathInput');
        const subjectInput = document.getElementById('configSubjectInput');
        const examInput = document.getElementById('configExamInput');
        const badgePath = document.getElementById('configBadgePath');
        const displaySubject = document.getElementById('configDisplaySubject');
        const badgeExam = document.getElementById('configBadgeExam');
        const availableText = document.getElementById('configAvailableCountText');

        const countRadios = document.querySelectorAll('.config-count-radio');
        const customCountWrapper = document.getElementById('customCountWrapper');
        const customCountInput = document.getElementById('customCountInput');

        const timeRadios = document.querySelectorAll('.config-time-radio');
        const customTimeWrapper = document.getElementById('customTimeWrapper');
        const customTimeInput = document.getElementById('customTimeInput');

        const diffRadios = document.querySelectorAll('.config-diff-radio');

        function fetchAvailableCount() {
            if (!availableText) return;
            const path = pathInput ? pathInput.value : 'college';
            const subject = subjectInput ? subjectInput.value : '';
            const exam = examInput ? examInput.value : '';
            let selectedDiff = 'All';
            diffRadios.forEach(r => { if (r.checked) selectedDiff = r.value; });

            availableText.innerHTML = '<span class="spinner-border spinner-border-sm text-secondary" role="status"></span> Checking bank...';

            const url = `/api/quiz/available_count?path=${encodeURIComponent(path)}&subject=${encodeURIComponent(subject)}&exam=${encodeURIComponent(exam)}&difficulty=${encodeURIComponent(selectedDiff)}`;
            fetch(url)
                .then(res => res.json())
                .then(data => {
                    const count = data.available || 0;
                    availableText.textContent = `${count} question${count === 1 ? '' : 's'} available`;
                })
                .catch(() => {
                    availableText.textContent = 'Question bank ready';
                });
        }

        // When modal is shown via Bootstrap trigger
        quizModalEl.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (button) {
                const path = button.dataset.path || 'college';
                const subject = button.dataset.subject || 'Python Programming';
                const exam = button.dataset.exam || '';

                if (pathInput) pathInput.value = path;
                if (subjectInput) subjectInput.value = subject;
                if (examInput) examInput.value = exam;

                if (badgePath) {
                    badgePath.textContent = path === 'competitive' ? 'Competitive Prep' : 'College Track';
                    badgePath.className = path === 'competitive' ? 'badge bg-teal text-white me-2 px-2 py-1' : 'badge bg-primary text-white me-2 px-2 py-1';
                }
                if (displaySubject) displaySubject.textContent = subject;

                if (badgeExam) {
                    if (exam) {
                        badgeExam.textContent = exam;
                        badgeExam.classList.remove('d-none');
                    } else {
                        badgeExam.classList.add('d-none');
                    }
                }

                // Set defaults based on track
                if (path === 'competitive') {
                    const time15Radio = document.getElementById('time_15');
                    if (time15Radio) {
                        time15Radio.checked = true;
                        if (customTimeWrapper) customTimeWrapper.classList.add('d-none');
                        if (customTimeInput) customTimeInput.value = '15';
                    }
                } else {
                    const time0Radio = document.getElementById('time_0');
                    if (time0Radio) {
                        time0Radio.checked = true;
                        if (customTimeWrapper) customTimeWrapper.classList.add('d-none');
                        if (customTimeInput) customTimeInput.value = '0';
                    }
                }

                // Default count to 10
                const count10Radio = document.getElementById('count_10');
                if (count10Radio) {
                    count10Radio.checked = true;
                    if (customCountWrapper) customCountWrapper.classList.add('d-none');
                    if (customCountInput) customCountInput.value = '10';
                }

                fetchAvailableCount();
            }
        });

        // Count radio listeners
        countRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                if (this.value === 'custom') {
                    if (customCountWrapper) {
                        customCountWrapper.classList.remove('d-none');
                        if (customCountInput) customCountInput.focus();
                    }
                } else {
                    if (customCountWrapper) customCountWrapper.classList.add('d-none');
                    if (customCountInput) customCountInput.value = this.value;
                }
            });
        });

        // Time radio listeners
        timeRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                if (this.value === 'custom') {
                    if (customTimeWrapper) {
                        customTimeWrapper.classList.remove('d-none');
                        if (customTimeInput) customTimeInput.focus();
                    }
                } else {
                    if (customTimeWrapper) customTimeWrapper.classList.add('d-none');
                    if (customTimeInput) customTimeInput.value = this.value;
                }
            });
        });

        // Difficulty radio listeners
        diffRadios.forEach(radio => {
            radio.addEventListener('change', fetchAvailableCount);
        });
    }

    // 4. Global Resource Bookmark Toggle Button Handler
    const bookmarkBtns = document.querySelectorAll('.toggle-bookmark-btn');
    bookmarkBtns.forEach(btn => {
        btn.addEventListener('click', async function (e) {
            e.preventDefault();
            const resId = this.dataset.id;
            const icon = this.querySelector('i');
            try {
                const res = await fetch(`/api/resources/${resId}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'toggle_bookmark' })
                });
                const data = await res.json();
                if (data.success && icon) {
                    if (data.is_bookmarked) {
                        icon.className = 'bi bi-bookmark-fill text-warning';
                    } else {
                        icon.className = 'bi bi-bookmark';
                    }
                }
            } catch (err) {
                console.error('Bookmark toggle error:', err);
            }
        });
    });

    // 5. Global Responsive Light / Dark Theme Toggle
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeToggleIcon = document.getElementById('themeToggleIcon');

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('edumentor_theme', theme);
        if (themeToggleIcon) {
            if (theme === 'dark') {
                themeToggleIcon.className = 'bi bi-sun-fill text-warning';
            } else {
                themeToggleIcon.className = 'bi bi-moon-stars-fill';
            }
        }
    }

    // Apply stored theme if present on page load
    const savedTheme = localStorage.getItem('edumentor_theme');
    if (savedTheme) {
        applyTheme(savedTheme);
    } else {
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        if (themeToggleIcon) {
            themeToggleIcon.className = currentTheme === 'dark' ? 'bi bi-sun-fill text-warning' : 'bi bi-moon-stars-fill';
        }
    }

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);

            // Sync with backend if logged in
            fetch('/settings/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new URLSearchParams({ theme_preference: newTheme })
            }).catch(function () {
                // Ignore silent network failure if unauthenticated
            });
        });
    }
});


