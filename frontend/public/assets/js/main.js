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
    // Ensure the top-left logo/brand links to home
    ensureNavBrandLink();

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

// Make the navbar brand (logo + name) a link to the home page across pages
function ensureNavBrandLink() {
    const navBrand = document.querySelector('.nav .nav-brand') || document.querySelector('.nav-brand');
    if (!navBrand) return;

    // Compute asset path relative to current pages directory
    const logoSrc = '../public/assets/img/logo.png';
    const homeHref = 'index.html';

    let link = navBrand.querySelector('a');
    if (!link) {
        // Create a single anchor and move existing children into it to avoid duplicates
        link = document.createElement('a');
        link.setAttribute('href', homeHref);
        link.setAttribute('aria-label', 'CompliCopilot Home');
        while (navBrand.firstChild) {
            link.appendChild(navBrand.firstChild);
        }
        navBrand.appendChild(link);
    } else {
        // Normalize attributes and remove any duplicate siblings outside the link
        link.setAttribute('href', homeHref);
        link.setAttribute('aria-label', 'CompliCopilot Home');
        Array.from(navBrand.children).forEach(child => {
            if (child !== link) navBrand.removeChild(child);
        });
    }

    // Ensure there is exactly one logo inside the link
    let img = link.querySelector('img.logo') || link.querySelector('img');
    if (!img) {
        img = document.createElement('img');
        img.className = 'logo';
        img.src = logoSrc;
        img.alt = 'CompliCopilot logo';
        link.insertBefore(img, link.firstChild);
    } else {
        img.classList.add('logo');
        if (!img.getAttribute('src')) img.src = logoSrc;
        if (!img.getAttribute('alt')) img.alt = 'CompliCopilot logo';
    }

    // Ensure brand text exists once inside the link
    let name = link.querySelector('.brand-name');
    if (!name) {
        name = document.createElement('span');
        name.className = 'brand-name';
        name.textContent = 'CompliCopilot';
        link.appendChild(name);
    }
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
    const authForm = document.querySelector('.auth-form') || document.getElementById('auth-form');
    const authContainer = document.querySelector('.auth-container');
    const authOverlay = document.getElementById('auth-loading');

    // Cursor-tracked ambient light
    if (authContainer) {
        let targetX = 0.5, targetY = 0.2;
        let currentX = targetX, currentY = targetY;
        const ease = 0.15;
        let hasFocus = false;
        const step = () => {
            currentX += (targetX - currentX) * ease;
            currentY += (targetY - currentY) * ease;
            authContainer.style.setProperty('--spot-x', (currentX*100).toFixed(2)+'%');
            authContainer.style.setProperty('--spot-y', (currentY*100).toFixed(2)+'%');
            requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
        authContainer.addEventListener('mousemove', (e) => {
            const r = authContainer.getBoundingClientRect();
            targetX = Math.min(Math.max((e.clientX - r.left) / r.width, 0), 1);
            targetY = Math.min(Math.max((e.clientY - r.top) / r.height, 0), 1);
            if (!hasFocus) {
                authContainer.style.setProperty('--spot-a', '0.30');
                clearTimeout(step._t);
                step._t = setTimeout(() => authContainer.style.setProperty('--spot-a','0.24'), 220);
            }
        });
        authContainer.addEventListener('mouseleave', ()=>{ targetX=0.5; targetY=0.2; });
        authContainer.addEventListener('focusin', ()=>{ hasFocus=true; authContainer.style.setProperty('--spot-a','0.20'); });
        authContainer.addEventListener('focusout', ()=>{ hasFocus=false; authContainer.style.setProperty('--spot-a','0.24'); });
    }

    // Tab switching (safe if only signin exists)
    const signinFormEl = document.getElementById('signin-form');
    const signupFormEl = document.getElementById('signup-form');
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            formContents.forEach(c => c.classList.remove('active'));
            if (targetTab === 'signin' && signinFormEl) {
                signinFormEl.classList.add('active');
                authTitle && (authTitle.textContent = 'Welcome Back');
                authSubtitle && (authSubtitle.textContent = 'Sign in to your CompliCopilot account');
                authContainer && authContainer.classList.remove('glow-strong');
            } else if (targetTab === 'signup' && signupFormEl) {
                signupFormEl.classList.add('active');
                authTitle && (authTitle.textContent = 'Create Account');
                authSubtitle && (authSubtitle.textContent = 'Join thousands of small businesses');
                authContainer && authContainer.classList.add('glow-strong');
            }
        });
    });

    // Form submission
    if (authForm) {
        authForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const submitButton = this.querySelector('button[type="submit"]');
            addLoadingState(submitButton);
            if (authOverlay) authOverlay.classList.add('active');

            // Determine if signup or signin
            const isSignup = this.id === 'signup-form';
            const url = isSignup
                ? 'http://127.0.0.1:8000/auth/signup'
                : 'http://127.0.0.1:8000/auth/signin';
            const formData = new FormData(this);
            const payload = {};
            formData.forEach((v, k) => payload[k] = v);

            try {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(payload)
                });
                const data = await res.json();
                removeLoadingState(submitButton);
                if (authOverlay) authOverlay.classList.remove('active');
                if (!res.ok) {
                    showNotification('Error', data.detail || 'Authentication failed', 'error');
                    return;
                }
                if (isSignup) {
                    showNotification('Success!', 'Account created. Please sign in.', 'success');
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    showNotification('Success!', 'Signed in successfully', 'success');
                    localStorage.setItem('ccp_token', data.access_token);
                    setTimeout(() => window.location.href = 'dashboard.html', 800);
                }
            } catch (err) {
                removeLoadingState(submitButton);
                if (authOverlay) authOverlay.classList.remove('active');
                showNotification('Error', 'Network error', 'error');
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
    // Existing avatar dropdown
    const userAvatar = document.querySelector('.user-avatar');
    const userDropdown = document.getElementById('user-dropdown');
    if (userAvatar && userDropdown) {
        userAvatar.addEventListener('click', () => userDropdown.classList.toggle('active'));
        document.addEventListener('click', (e) => {
            if (!userAvatar.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.classList.remove('active');
            }
        });
    }

    // Build store from current rows
    const tbody = document.getElementById('receipts-tbody') || document.querySelector('.table-body');
    const toData = () => {
        const rows = Array.from((tbody || document).querySelectorAll('.transaction-row'));
        return rows.map((row, i) => ({
            id: row.dataset.id || String(i+1),
            vendor: row.querySelector('.vendor-name')?.textContent.trim() || '',
            date: row.dataset.date || row.querySelector('.col-date')?.textContent.trim() || '',
            amount: parseFloat(row.dataset.amount || (row.querySelector('.col-amount')?.textContent.replace(/[^\d.]/g,'') || '0')),
            category: row.dataset.category || row.querySelector('.category-tag')?.className.split(' ').pop() || '',
            status: row.dataset.status || row.querySelector('.status-text')?.textContent.trim().toLowerCase() || '',
            gstin: row.dataset.gstin || '',
            filename: row.dataset.filename || ''
        }));
    };
    // Hydrate from localStorage any saved receipts from upload
    const saved = JSON.parse(localStorage.getItem('ccp_new_receipts') || '[]');
    const store = {
        all: toData().concat(saved),
        filtered: [],
        filters: { gstin: '' }
    };

    const countEl = document.getElementById('results-count');

    function applyFilters() {
        const q = (store.filters.gstin || '').replace(/\s+/g,'').toLowerCase();
        let data = [...store.all];
        if (q) data = data.filter(d => (d.gstin || '').replace(/\s+/g,'').toLowerCase().includes(q));
        store.filtered = data;
        renderTable(data);
        if (countEl) countEl.textContent = `${data.length} result${data.length===1?'':'s'}`;
    }

    function renderTable(data) {
        if (!tbody) return;
        tbody.innerHTML = '';
        data.forEach(item => {
            const row = document.createElement('div');
            row.className = 'transaction-row';
            row.dataset.id = item.id;
            row.dataset.status = item.status;
            row.dataset.category = item.category;
            row.dataset.date = item.date;
            row.dataset.amount = String(item.amount);
            row.dataset.gstin = item.gstin || '';
            row.dataset.filename = item.filename || '';
            row.innerHTML = `
                <div class="col-vendor">
                    <div class="vendor-info">
                        <div class="vendor-name">${item.vendor}</div>
                        <div class="vendor-detail">${item.category ? item.category.charAt(0).toUpperCase()+item.category.slice(1) : ''}</div>
                    </div>
                </div>
                <div class="col-date">${item.date}</div>
                <div class="col-amount">₹${item.amount.toLocaleString()}</div>
                <div class="col-category"><span class="category-tag ${item.category || 'uncategorized'}">${item.category || 'Uncategorized'}</span></div>
                <div class="col-status">
                    <span class="status-dot ${item.status.replace(' ','-')}"></span>
                    <span class="status-text">${item.status.replace('-', ' ')}</span>
                </div>
            `;
            row.addEventListener('click', () => openDrawer(item));
            tbody.appendChild(row);
        });
    }

    // Wire only GSTIN search and CSV export
    const $ = (s)=>document.getElementById(s);
    const gstinInput = $('filter-search');
    const exportBtn = $('export-csv');
    const genReport = document.getElementById('generate-report');

    gstinInput && gstinInput.addEventListener('input', (e)=>{
        store.filters.gstin = e.target.value.trim();
        applyFilters();
    });

    exportBtn && exportBtn.addEventListener('click', ()=>{
        const rows = store.filtered.length ? store.filtered : store.all;
        const header = ['Vendor','Date','Amount','Category','Status','GSTIN'];
        const csv = [header.join(',')]
            .concat(rows.map(r =>
                `"${(r.vendor||'').replace(/"/g,'""')}",${r.date||''},${r.amount||0},"${r.category||''}",${r.status||''},"${r.gstin||''}"`
            ))
            .join('\n');
        const blob = new Blob([csv], {type:'text/csv;charset=utf-8;'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'receipts.csv';
        a.click();
        URL.revokeObjectURL(a.href);
    });

    // Generate Google Docs-style report (HTML .doc download)
    genReport && genReport.addEventListener('click', (e)=>{
        e.preventDefault();
        const rows = store.filtered.length ? store.filtered : store.all;
        const html = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>CompliCopilot Report</title>
        <style>
            body{font-family:Arial,Helvetica,sans-serif;line-height:1.5;color:#111}
            h1{font-size:22px;margin:16px 0}
            table{border-collapse:collapse;width:100%;font-size:14px}
            th,td{border:1px solid #ccc;padding:8px;text-align:left}
            th{background:#f2f2f2}
        </style></head><body>
        <h1>CompliCopilot Expense Report</h1>
        <table><thead><tr>
            <th>Vendor</th><th>Date</th><th>Amount (₹)</th><th>Category</th><th>Status</th><th>GSTIN</th>
        </tr></thead><tbody>
        ${rows.map(r => `<tr><td>${escapeHtml(r.vendor||'')}</td><td>${escapeHtml(r.date||'')}</td><td>${(r.amount||0).toLocaleString()}</td><td>${escapeHtml(r.category||'')}</td><td>${escapeHtml(r.status||'')}</td><td>${escapeHtml(r.gstin||'')}</td></tr>`).join('')}
        </tbody></table>
        </body></html>`;
        const blob = new Blob([html], {type:'application/msword'});
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'CompliCopilot-Report.doc';
        a.click();
        URL.revokeObjectURL(a.href);
    });

    // Drawer
    const drawer = document.getElementById('receipt-drawer');
    const drawerBody = document.getElementById('drawer-body');
    function openDrawer(item) {
        if (!drawer || !drawerBody) return;
        drawer.classList.add('active');
        drawer.setAttribute('aria-hidden','false');
        drawerBody.innerHTML = `
            <div class="drawer-field">
                <label>Vendor</label>
                <input type="text" value="${item.vendor}">
            </div>
            <div class="drawer-field">
                <label>Date</label>
                <input type="text" value="${item.date}">
            </div>
            <div class="drawer-field">
                <label>Amount</label>
                <input type="text" value="₹${item.amount.toLocaleString()}">
            </div>
            <div class="drawer-field">
                <label>Category</label>
                <select>
                    <option ${item.category==='meals'?'selected':''}>meals</option>
                    <option ${item.category==='transport'?'selected':''}>transport</option>
                    <option ${item.category==='software'?'selected':''}>software</option>
                    <option ${item.category==='fuel'?'selected':''}>fuel</option>
                    <option ${item.category==='uncategorized'?'selected':''}>uncategorized</option>
                </select>
            </div>
            <div class="drawer-actions">
                <button class="btn-secondary" data-close-drawer>Close</button>
                <button class="btn-primary">Save</button>
            </div>
        `;
    }
    drawer && drawer.addEventListener('click', (e)=>{
        if (e.target.matches('[data-close-drawer]')) {
            drawer.classList.remove('active');
            drawer.setAttribute('aria-hidden','true');
        }
    });

    // Initial render
    applyFilters();
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
            
            // Simulate saving then redirect to dashboard with updated data
            setTimeout(() => {
                removeLoadingState(submitButton);
                // Collect review data
                const newReceipt = {
                    id: String(Date.now()),
                    vendor: (document.getElementById('vendor-name')?.value || '').trim() || 'Unknown Vendor',
                    date: document.getElementById('receipt-date')?.value || new Date().toISOString().slice(0,10),
                    amount: parseFloat(document.getElementById('total-amount')?.value || '0') || 0,
                    category: document.getElementById('expense-category')?.value || 'uncategorized',
                    status: 'approved',
                    gstin: document.getElementById('gst-number')?.value || '',
                    filename: 'uploaded-' + (document.getElementById('file-input')?.files?.[0]?.name || 'receipt')
                };
                const existing = JSON.parse(localStorage.getItem('ccp_new_receipts') || '[]');
                existing.unshift(newReceipt);
                localStorage.setItem('ccp_new_receipts', JSON.stringify(existing));
                // Navigate back to dashboard
                window.location.href = 'dashboard.html';
            }, 1200);
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
                const step = processSteps[currentStep];
                step.classList.add('active');
                const icon = step.querySelector('.process-icon');
                if (icon) {
                    if (currentStep === 0) icon.textContent = '✓';
                    else icon.textContent = '⟳';
                }
                currentStep++;
            } else {
                clearInterval(processInterval);
                processSteps.forEach((s, i) => {
                    const icon = s.querySelector('.process-icon');
                    if (icon) icon.textContent = '✓';
                    s.classList.add('active');
                });
                // Load preview and move to review
                loadReceiptPreview(file);
                showStep('review');
                updateProgressStep(3);
            }
        }, 700);
    }
    
    function loadReceiptPreview(file) {
        const previewImg = document.getElementById('receipt-preview');
        if (!previewImg) return;
        if (file && file.type && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => { previewImg.src = e.target.result; };
            reader.readAsDataURL(file);
        } else {
            previewImg.src = '../public/assets/img/logo.png';
        }
    }

    function showStep(stepName) {
        const ids = ['upload','processing','review','success'];
        ids.forEach(id => {
            const el = document.getElementById(`${id}-step`);
            if (!el) return;
            el.classList.toggle('active', id === stepName);
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

// Small HTML escaper for report generation
function escapeHtml(s){
    return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[c]));
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