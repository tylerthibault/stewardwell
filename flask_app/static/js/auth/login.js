class LoginManager {
    constructor() {
        this.initializeElements();
        this.setupEventListeners();
        this.setupCodeInputs();
    }

    initializeElements() {
        this.roleButtons = document.querySelectorAll('.role-button');
        this.codeInputs = document.querySelectorAll('.code-input');
        this.backButton = document.querySelector('.back-button');
        this.steps = {
            role: document.getElementById('roleStep'),
            parentLogin: document.getElementById('parentLoginStep'),
            childLogin1: document.getElementById('childLoginStep1'),
            childLogin2: document.getElementById('childLoginStep2')
        };
    }

    setupEventListeners() {
        // Role selection handlers
        this.roleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const role = button.dataset.role;
                if (role === 'parent') {
                    this.showParentLogin();
                } else {
                    this.showChildLogin();
                }
            });
        });

        // Back button handler
        if (this.backButton) {
            this.backButton.addEventListener('click', () => this.showRoleSelection());
        }

        // Next button in child login
        const nextButton = document.querySelector('#childLoginStep1 .auth-submit');
        if (nextButton) {
            nextButton.addEventListener('click', () => this.showChildStep2());
        }
    }

    setupCodeInputs() {
        this.codeInputs.forEach((input, index) => {
            input.addEventListener('keyup', (e) => {
                if (e.key >= 0 && e.key <= 9) {
                    if (index < this.codeInputs.length - 1) {
                        this.codeInputs[index + 1].focus();
                    }
                } else if (e.key === 'Backspace') {
                    if (index > 0) {
                        this.codeInputs[index - 1].focus();
                    }
                }
            });

            // Paste handling for code inputs
            input.addEventListener('paste', (e) => {
                e.preventDefault();
                const paste = (e.clipboardData || window.clipboar
