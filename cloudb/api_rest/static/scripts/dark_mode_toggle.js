// dark_mode_toggle.js
const themeToggle = document.getElementById('theme-toggle');
const html = document.documentElement;

// Carregar estado inicial do localStorage
if (localStorage.getItem('theme') === 'dark') {
    html.classList.add('dark');
    themeToggle.checked = true;
}

// Alternar o tema
themeToggle.addEventListener('change', () => {
    if (themeToggle.checked) {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
    }
});