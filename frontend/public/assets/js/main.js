// Main JavaScript for CompliCopilot

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize based on current page
    const currentPage = window.location.pathname.split('/').pop();
    
    switch(currentPage) {
        case 'index.html':
        case '':
            initLandingPage();
            break;
        case 'auth.html':
            initAuthPage();
            break;
        case 'dashboard.html':
            initDashboard();
            break;
        case 'upload.html':
            initUploadPage();
            break;
    }
    
    // Global initializations
    initGlobalFeatures();
});

// Global Features
function initGlobalFeatures() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading states to buttons
    document.querySelectorAll('button[type="submit"]').forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.form && this.form.checkValidity()) {
                addLoadingState(this);
            }
        });
    });
}

// Landing Page Initialization
function initLandingPage() {
    // Animate feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
                entry.target.style.animationDelay = `${Array.from(featureCards).indexOf(entry.target) * 0.1}s`;
            }
        });
    }, observerOptions);
    
    featureCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        observer.observe(card);
    });
    
    // Add CSS animation keyframes
    if (!document.querySelector('#landing-animations')) {
        const style = document.createElement('style');
        style.id = 'landing-animations';
        style.textContent = `
            @keyframes fadeInUp {
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Authentication Page Initialization
function initAuthPage() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const formContents = document.querySelectorAll('.form-content');
    const authTitle = document.getElementById('auth-title');
    const authSubtitle = document.getElementById('auth-subtitle');
    // Support both id="auth-form" and class="auth-form"
    const authForm = document.querySelector('.auth-form') || document.getElementById('auth-form');
    const authContainer = document.querySelector('.auth-container');
    const authOverlay = document.getElementById('auth-loading');

    // Cursor-tracked ambient light: smoothly follow pointer inside container
    if (authContainer) {
        let targetX = 0.5, targetY = 0.5; // 0..1
        let currentX = targetX, currentY = targetY;
        const ease = 0.15;
        let hasFocus = false;

        const updateVars = () => {
            currentX += (targetX - currentX) * ease;
            currentY += (targetY - currentY) * ease;
            const xPerc = (currentX * 100).toFixed(2) + '%';
            const yPerc = (currentY * 100).toFixed(2) + '%';
            authContainer.style.setProperty('--spot-x', xPerc);
            authContainer.style.setProperty('--spot-y', yPerc);
            requestAnimationFrame(updateVars);
        };
        requestAnimationFrame(updateVars);

        const setTarget = (e) => {
            const rect = authContainer.getBoundingClientRect();
            const x = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1);
            const y = Math.min(Math.max((e.clientY - rect.top) / rect.height, 0), 1);
            targetX = x; targetY = y;
            // lift intensity slightly when moving (unless an input is focused)
            if (!hasFocus) {
                authContainer.style.setProperty('--spot-a', '0.30');
                clearTimeout(setTarget._t);
                setTarget._t = setTimeout(() => authContainer.style.setProperty('--spot-a', '0.24'), 220);
            }
        };

        authContainer.addEventListener('mousemove', setTarget);
        authContainer.addEventListener('mouseleave', () => {
            targetX = 0.5; targetY = 0.5; // center
        });

        // While typing/focused, keep the glow calmer and pause boosts
        authContainer.addEventListener('focusin', () => {
            hasFocus = true;
            authContainer.style.setProperty('--spot-a', '0.20');
        });
        authContainer.addEventListener('focusout', () => {
            hasFocus = false;
            authContainer.style.setProperty('--spot-a', '0.24');
        });
    }
    
    // Tab switching
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            
            // Update active tab
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update form content
            formContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${targetTab}-form`).classList.add('active');
            
            // Update title and subtitle
            if (targetTab === 'signin') {
                authTitle.textContent = 'Welcome Back';
                authSubtitle.textContent = 'Sign in to your CompliCopilot account';
                authContainer && authContainer.classList.remove('glow-strong');
            } else {
                authTitle.textContent = 'Create Account';
                authSubtitle.textContent = 'Join thousands of small businesses';
                authContainer && authContainer.classList.add('glow-strong');
            }
        });
    });
    
    // Form submission (guarded if the form is present)
    if (authForm) {
        authForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const activeTab = document.querySelector('.tab-btn.active').getAttribute('data-tab');
            const submitButton = this.querySelector('button[type="submit"]');
            
            addLoadingState(submitButton);
            if (authOverlay) authOverlay.classList.add('active');
            
            // Simulate API call
            setTimeout(() => {
                removeLoadingState(submitButton);
                if (authOverlay) authOverlay.classList.remove('active');
                
                // Simulate successful authentication
                showNotification('Success!', `Account ${activeTab === 'signin' ? 'signed in' : 'created'} successfully`, 'success');
                
                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 1500);
            }, 2000);
        });
    }
    
    // Password confirmation validation for signup
    const signupConfirm = document.getElementById('signup-confirm');
    const signupPassword = document.getElementById('signup-password');
    
    if (signupConfirm && signupPassword) {
        signupConfirm.addEventListener('input', function() {
            if (this.value !== signupPassword.value) {
                this.setCustomValidity('Passwords do not match');
            } else {
                this.setCustomValidity('');
            }
        });
        
        signupPassword.addEventListener('input', function() {
            if (signupConfirm.value && signupConfirm.value !== this.value) {
                signupConfirm.setCustomValidity('Passwords do not match');
            } else {
                signupConfirm.setCustomValidity('');
            }
        });
    }
    
        // Dev admin shortcut
        const devBtn = document.getElementById('dev-admin-btn');
        if (devBtn) {
            devBtn.addEventListener('click', () => {
                const user = { name: 'Admin', email: 'admin@complicopilot.dev', role: 'admin' };
                localStorage.setItem('ccp_user', JSON.stringify(user));
                showNotification('Signed in', 'Developer admin session started', 'success');
                setTimeout(() => window.location.href = 'dashboard.html', 600);
            });
        }
}

// Dashboard Initialization
function initDashboard() {
    // User menu toggle
    const userAvatar = document.querySelector('.user-avatar');
    const userDropdown = document.getElementById('user-dropdown');
    
    if (userAvatar && userDropdown) {
        userAvatar.addEventListener('click', () => {
            userDropdown.classList.toggle('active');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('active');
            }
        });
    }
    
    // Animate overview cards
    const overviewCards = document.querySelectorAll('.overview-card');
    
    overviewCards.forEach((card, index) => {
        card.style.animation = 'slideInFromLeft 0.6s ease-out forwards';
        card.style.animationDelay = `${index * 0.1}s`;
    });
    
    // Transaction row interactions
    const transactionRows = document.querySelectorAll('.transaction-row');
    
    transactionRows.forEach(row => {
        row.addEventListener('click', function() {
            // Simulate opening transaction details
            showNotification('Transaction Details', 'Opening transaction details...', 'info');
        });
    });
    
    // Add CSS animations for dashboard
    if (!document.querySelector('#dashboard-animations')) {
        const style = document.createElement('style');
        style.id = 'dashboard-animations';
        style.textContent = `
            @keyframes slideInFromLeft {
                from {
                    opacity: 0;
                    transform: translateX(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Upload Page Initialization
function initUploadPage() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStep = document.getElementById('upload-step');
    const processingStep = document.getElementById('processing-step');
    const reviewStep = document.getElementById('review-step');
    const successStep = document.getElementById('success-step');
    const reviewForm = document.getElementById('review-form');
    
    // File upload functionality
    if (dropZone && fileInput) {
        // Click to upload
        dropZone.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Drag and drop
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }
    
    // Form submission for review
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitButton = this.querySelector('button[type="submit"]');
            addLoadingState(submitButton);
            
            // Simulate saving
            setTimeout(() => {
                removeLoadingState(submitButton);
                showStep('success');
                updateProgressStep(4);
            }, 2000);
        });
    }
    
    // File upload handler
    function handleFileUpload(file) {
        // Validate file type
        const validTypes = ['image/jpeg', 'image/png', 'application/pdf'];
        if (!validTypes.includes(file.type)) {
            showNotification('Invalid File', 'Please upload a JPG, PNG, or PDF file', 'error');
            return;
        }
        
        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
            showNotification('File Too Large', 'Please upload a file smaller than 10MB', 'error');
            return;
        }
        
        // Show processing step
        showStep('processing');
        updateProgressStep(2);
        
        // Simulate file processing
        simulateProcessing(file);
    }
    
    // Simulate AI processing
    function simulateProcessing(file) {
        const processSteps = document.querySelectorAll('.process-item');
        let currentStep = 0;
        
        const processInterval = setInterval(() => {
            if (currentStep < processSteps.length) {
                processSteps[currentStep].classList.add('active');
                
                // Update process icon
                const icon = processSteps[currentStep].querySelector('.process-icon');
                if (currentStep === processSteps.length - 1) {
                    icon.textContent = '✓';
                } else {
                    icon.textContent = '⟳';
                }
                
                currentStep++;
            } else {
                clearInterval(processInterval);
                
                // Mark all as complete
                processSteps.forEach(step => {
                    const icon = step.querySelector('.process-icon');
                    icon.textContent = '✓';
                    step.classList.add('active');
                });
                
                // Move to review step
                setTimeout(() => {
                    showStep('review');
                    updateProgressStep(3);
                    loadReceiptPreview(file);
                }, 1000);
            }
        }, 800);
    }
    
    // Load receipt preview
    function loadReceiptPreview(file) {
        const previewImg = document.getElementById('receipt-preview');
        if (previewImg && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImg.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else if (previewImg) {
            // For PDF or other files, show placeholder
            previewImg.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjI1MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjMjQyNDI0Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzY2NjY2NiIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRvY3VtZW50IFByZXZpZXc8L3RleHQ+PC9zdmc+';
        }
    }
    
    // Step navigation
    function showStep(stepName) {
        const steps = ['upload', 'processing', 'review', 'success'];
        steps.forEach(step => {
            const element = document.getElementById(`${step}-step`);
            if (element) {
                element.classList.toggle('active', step === stepName);
            }
        });
    }
    
    // Update progress indicator
    function updateProgressStep(stepNumber) {
        const steps = document.querySelectorAll('.step');
        steps.forEach((step, index) => {
            step.classList.toggle('active', index + 1 <= stepNumber);
        });
    }
}

// Global helper functions
function toggleUserMenu() {
    const dropdown = document.getElementById('user-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

function goBackToUpload() {
    const uploadStep = document.getElementById('upload-step');
    const reviewStep = document.getElementById('review-step');
    
    if (uploadStep && reviewStep) {
        uploadStep.classList.add('active');
        reviewStep.classList.remove('active');
        updateProgressStep(1);
    }
}

function uploadAnother() {
    // Reset form and go back to upload
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.value = '';
    }
    
    goBackToUpload();
}

function updateProgressStep(stepNumber) {
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.classList.toggle('active', index + 1 <= stepNumber);
    });
}

// Loading state management
function addLoadingState(button) {
    if (button.querySelector('.loading-spinner')) return;

    const originalText = button.textContent;
    button.setAttribute('data-original-text', originalText);
    button.disabled = true;

    const spinner = document.createElement('span');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '⟳';
    spinner.style.cssText = `
        display: inline-block;
        animation: spin 1s linear infinite;
        margin-right: 8px;
    `;

    // Replace button content with spinner + text
    button.textContent = '';
    button.appendChild(spinner);
    const loadingText = document.createElement('span');
    loadingText.textContent = 'Processing...';
    button.appendChild(loadingText);
}

function removeLoadingState(button) {
    const originalText = button.getAttribute('data-original-text');
    button.disabled = false;
    if (originalText !== null) {
        button.textContent = originalText;
        button.removeAttribute('data-original-text');
    }
}

// Simple toast notifications
function showNotification(title, message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 16px;
            right: 16px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            z-index: 9999;
        `;
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    const bg = type === 'success' ? 'rgba(0,255,136,0.15)' : type === 'error' ? 'rgba(255,71,87,0.15)' : 'rgba(0,212,255,0.12)';
    const border = type === 'success' ? '#00ff88' : type === 'error' ? '#ff4757' : '#00d4ff';
    toast.style.cssText = `
        min-width: 260px;
        max-width: 360px;
        padding: 12px 14px;
        border-radius: 10px;
        background: ${bg};
        border: 1px solid ${border};
        color: #fff;
        box-shadow: 0 6px 24px rgba(0,0,0,0.25);
        backdrop-filter: blur(6px);
        animation: toast-in 180ms ease-out;
    `;
    toast.innerHTML = `
        <div style="font-weight:600;margin-bottom:4px;">${title}</div>
        <div style="opacity:.85;font-size:14px;">${message}</div>
    `;
    if (!document.getElementById('toast-keyframes')) {
        const style = document.createElement('style');
        style.id = 'toast-keyframes';
        style.textContent = `@keyframes toast-in { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: translateY(0); } }`;
        document.head.appendChild(style);
    }
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.transition = 'opacity 200ms ease, transform 200ms ease';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-6px)';
        setTimeout(() => toast.remove(), 220);
    }, 2800);
}

// Cursor tracing light: fluid, non-blocking, rAF-driven
(function setupCursorLight() {
  // Avoid duplicate init
  if (window.__ccpCursorLightInitialized) return;
  window.__ccpCursorLightInitialized = true;

  const isTouch = matchMedia('(pointer: coarse)').matches || 'ontouchstart' in window;
  const prefersReduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Disable on touch devices or when user prefers reduced motion
  if (isTouch || prefersReduced) return;

  // Create or reuse the overlay element
  let light = document.querySelector('.cursor-light');
  if (!light) {
    light = document.createElement('div');
    light.className = 'cursor-light';
    document.body.appendChild(light);
  }

  let lastX = -9999;
  let lastY = -9999;
  let rafId = null;
  let needsUpdate = false;
  let paused = false;

  function onMouseMove(e) {
    lastX = e.clientX;
    lastY = e.clientY;
    if (!rafId) {
      rafId = requestAnimationFrame(tick);
    }
  }

  function tick() {
    rafId = null;
    if (paused) return;
    // Use CSS variables to avoid layout thrash
    document.documentElement.style.setProperty('--cursor-x', lastX + 'px');
    document.documentElement.style.setProperty('--cursor-y', lastY + 'px');
    // If mouse keeps moving, schedule next frame
    if (needsUpdate) {
      needsUpdate = false;
      rafId = requestAnimationFrame(tick);
    }
  }

  // Use passive listener; minimal work in handler
  window.addEventListener('mousemove', (e) => {
    onMouseMove(e);
    // coalesce moves between frames
    needsUpdate = true;
  }, { passive: true });

  // Reduce intensity while focusing inputs (esp. on auth page)
  const root = document.documentElement;
  function dimLight() {
    root.style.setProperty('--cursor-light-opacity', '0.15');
  }
  function restoreLight() {
    root.style.setProperty('--cursor-light-opacity', '0.6');
  }
  // Pause position updates while typing in inputs/textareas/selects for extra safety
  function focusIn(e) {
    if (e.target && /^(INPUT|TEXTAREA|SELECT)$/i.test(e.target.tagName)) {
      paused = true;
      dimLight();
    }
  }
  function focusOut(e) {
    if (e.target && /^(INPUT|TEXTAREA|SELECT)$/i.test(e.target.tagName)) {
      paused = false;
      restoreLight();
      // Kick a position update after resume
      if (!rafId) rafId = requestAnimationFrame(tick);
    }
  }
  document.addEventListener('focusin', focusIn, true);
  document.addEventListener('focusout', focusOut, true);

  // Hide effect if the page explicitly opts out (optional: add data attribute on auth page container)
  const authLike = document.querySelector('[data-page="auth"], .auth-page, body[data-route="auth"]');
  if (authLike && isSmallScreen()) {
    light.style.display = 'none';
  }

  // Cleanup on SPA-like navigation (if applicable)
  window.addEventListener('beforeunload', () => {
    window.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('focusin', focusIn, true);
    document.removeEventListener('focusout', focusOut, true);
    if (rafId) cancelAnimationFrame(rafId);
  });

  function isSmallScreen() {
    return window.innerWidth < 768 || window.innerHeight < 500;
  }
})();

// Ensure global init calls above on DOM ready if you have an init function:
// If you have initGlobalFeatures(), keep calling it. Otherwise DOMContentLoaded is fine.
document.addEventListener('DOMContentLoaded', () => {
  // setupCursorLight runs immediately via IIFE above
  // ...existing code...
});