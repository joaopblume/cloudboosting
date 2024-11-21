const themeToggle = document.getElementById('theme-toggle');
const htmlElement = document.documentElement;

// Verificar se o dark mode já foi ativado anteriormente
if (localStorage.getItem('theme') === 'dark') {
htmlElement.classList.add('dark');
themeToggle.checked = true; // Marca o toggle como "on"
}

// Toggle do dark mode
themeToggle.addEventListener('change', () => {
if (themeToggle.checked) {
    htmlElement.classList.add('dark');
    localStorage.setItem('theme', 'dark'); // Salva como "dark"
} else {
    htmlElement.classList.remove('dark');
    localStorage.setItem('theme', 'light'); // Salva como "light"
}
});