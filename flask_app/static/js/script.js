// Theme Management
class ThemeManager {
    constructor() {
        this.themeToggle = document.getElementById('theme-toggle');
        this.themeIcon = this.themeToggle.querySelector('i');
        this.init();
    }

    init() {
        this.checkSavedTheme();
        this.setupEventListeners();
    }

    updateThemeIcon(isDark) {
        this.themeIcon.className = isDark ? 'fas fa-sun' : 'fas fa-moon';
    }

    toggleTheme() {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        this.updateThemeIcon(isDarkMode);
    }

    checkSavedTheme() {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedTheme = localStorage.getItem('darkMode');
        
        if (savedTheme === 'true' || (savedTheme === null && prefersDark)) {
            document.body.classList.add('dark-mode');
            this.updateThemeIcon(true);
        }
    }

    setupEventListeners() {
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
    }
}

// Navigation Management
class NavigationManager {
    constructor() {
        this.navToggle = document.getElementById('nav-toggle');
        this.navMenu = document.getElementById('nav-menu');
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    toggleMenu() {
        this.navMenu.classList.toggle('active');
        const icon = this.navToggle.querySelector('i');
        icon.classList.toggle('fa-bars');
        icon.classList.toggle('fa-times');
    }

    setupEventListeners() {
        this.navToggle.addEventListener('click', () => this.toggleMenu());
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.navToggle.contains(e.target) && 
                !this.navMenu.contains(e.target) && 
                this.navMenu.classList.contains('active')) {
                this.toggleMenu();
            }
        });
    }
}

// Flash Messages Management
class FlashMessagesManager {
    constructor() {
        this.flashMessages = document.querySelectorAll('.flash-message');
        this.init();
    }

    init() {
        this.setupAutoDismiss();
    }

    setupAutoDismiss() {
        this.flashMessages.forEach(message => {
            setTimeout(() => {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }, 5000);
        });
    }
}

// Initialize all managers when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ThemeManager();
    new NavigationManager();
    new FlashMessagesManager();
});
