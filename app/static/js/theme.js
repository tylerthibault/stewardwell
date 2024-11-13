// Theme management
function setTheme(theme) {
    const html = document.documentElement;
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    // Remove all theme classes first
    html.classList.remove('light', 'dark');

    // Apply the appropriate theme
    if (theme === 'dark') {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    } else if (theme === 'light') {
        html.classList.add('light');
        localStorage.setItem('theme', 'light');
    } else if (theme === 'system') {
        const systemTheme = darkModeMediaQuery.matches ? 'dark' : 'light';
        html.classList.add(systemTheme);
        localStorage.setItem('theme', 'system');
    }

    // Update radio buttons if they exist
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    themeRadios.forEach(radio => {
        radio.checked = radio.value === theme;
    });

    // Save theme preference to server
    if (typeof updateUserTheme === 'function') {
        updateUserTheme(theme);
    }
}

// Function to update user theme preference on the server
function updateUserTheme(theme) {
    fetch('/settings/update-theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({ theme: theme })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Theme preference saved');
        }
    })
    .catch(error => console.error('Error saving theme preference:', error));
}

// Initialize theme
document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);

    // Listen for system theme changes if using system theme
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    darkModeMediaQuery.addListener((e) => {
        if (localStorage.getItem('theme') === 'system') {
            setTheme('system');
        }
    });

    // Add event listeners to theme radio buttons if they exist
    const themeRadios = document.querySelectorAll('input[name="theme"]');
    themeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.checked) {
                setTheme(e.target.value);
            }
        });
    });
});
