// Main JavaScript for CompliCopilot

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    // Handle Google OAuth2 redirect with token in URL
    if (window.location.pathname.endsWith('auth.html')) {
        const params = new URLSearchParams(window.location.search);
        const token = params.get('token');
        if (token) {
            localStorage.setItem('ccp_token', token);
            window.location.href = 'dashboard.html';
            return;
        }
    }
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
    
    // Removed global auto-loading state on submit buttons; handled within page-specific submit handlers
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
    function setActiveForm(target) {
        const isSignin = target === 'signin';
        if (signinFormEl) {
            signinFormEl.classList.toggle('active', isSignin);
            signinFormEl.querySelectorAll('input').forEach(inp => {
                if (isSignin) {
                    inp.removeAttribute('disabled');
                } else {
                    inp.setAttribute('disabled', 'disabled');
                }
            });
        }
        if (signupFormEl) {
            signupFormEl.classList.toggle('active', !isSignin);
            signupFormEl.querySelectorAll('input').forEach(inp => {
                if (!isSignin) {
                    inp.removeAttribute('disabled');
                } else {
                    inp.setAttribute('disabled', 'disabled');
                }
            });
        }
        if (isSignin) {
            authTitle && (authTitle.textContent = 'Welcome Back');
            authSubtitle && (authSubtitle.textContent = 'Sign in to your CompliCopilot account');
            authContainer && authContainer.classList.remove('glow-strong');
        } else {
            authTitle && (authTitle.textContent = 'Create Account');
            authSubtitle && (authSubtitle.textContent = 'Join thousands of small businesses');
            authContainer && authContainer.classList.add('glow-strong');
        }
    }
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetTab = button.getAttribute('data-tab');
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            setActiveForm(targetTab);
        });
    });
    // On page load, ensure only active form has required fields
    // Initialize forms: disable the inactive (signup initially)
    if (signinFormEl && signupFormEl) {
        setActiveForm('signin');
    }

    // Google login button - DISABLED: Using Firebase Auth instead
    // const googleBtn = document.querySelector('.btn-social.google');
    // if (googleBtn) {
    //     googleBtn.addEventListener('click', function(e) {
    //         e.preventDefault();
    //         window.location.href = 'http://localhost:8000/auth/google/login';
    //     });
    // }
    
    console.log("Note: Google OAuth handled by auth-google.js with Firebase Auth");
    
    // Form submission for Sign In and Sign Up
    if (authForm) {
        authForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            console.log('Form submitted!'); // Debug log
            const submitButton = this.querySelector('button[type="submit"]');
            // In case a global click handler added a loading state pre-emptively, clear it now
            removeLoadingState(submitButton);

            // Determine which form is active
            const isSignup = document.getElementById('signup-form').classList.contains('active');
            console.log('Is signup form:', isSignup); // Debug log
            
            // Frontend validation
            if (isSignup) {
                console.log('Validating signup form...'); // Debug log
                const email = document.getElementById('signup-email').value.trim();
                const password = document.getElementById('signup-password').value;
                const confirmPassword = document.getElementById('signup-confirm').value;
                const fullName = document.getElementById('signup-name').value.trim();
                const termsAccepted = document.querySelector('input[name="terms"]').checked;
                
                console.log('Form values:', { email, password, confirmPassword, fullName, termsAccepted }); // Debug log
                
                // Validate required fields
                if (!email || !password || !confirmPassword || !fullName) {
                    console.log('Required fields validation failed'); // Debug log
                    showNotification('Validation Error', 'Please fill in all required fields', 'error');
                    return;
                }
                
                // Validate email format
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(email)) {
                    console.log('Email validation failed'); // Debug log
                    showNotification('Validation Error', 'Please enter a valid email address', 'error');
                    return;
                }
                
                // Validate password match
                if (password !== confirmPassword) {
                    console.log('Password match validation failed'); // Debug log
                    showNotification('Validation Error', 'Passwords do not match', 'error');
                    return;
                }
                
                // Validate password strength
                if (password.length < 6) {
                    console.log('Password strength validation failed'); // Debug log
                    showNotification('Validation Error', 'Password must be at least 6 characters long', 'error');
                    return;
                }
                
                // Validate terms acceptance
                if (!termsAccepted) {
                    console.log('Terms validation failed'); // Debug log
                    showNotification('Validation Error', 'Please accept the Terms of Service', 'error');
                    return;
                }
                
                console.log('All validations passed!'); // Debug log
            } else {
                // Sign in validation
                const email = document.getElementById('signin-email').value.trim();
                const password = document.getElementById('signin-password').value;
                
                if (!email || !password) {
                    showNotification('Validation Error', 'Please enter both email and password', 'error');
                    return;
                }
            }
            
            addLoadingState(submitButton);
            if (authOverlay) authOverlay.classList.add('active');

            const url = isSignup
                ? 'http://localhost:8000/auth/signup'
                : 'http://localhost:8000/auth/signin';
            let payload = {};
            if (isSignup) {
                payload = {
                    email: document.getElementById('signup-email').value.trim(),
                    password: document.getElementById('signup-password').value,
                    full_name: document.getElementById('signup-name').value.trim()
                };
            } else {
                payload = {
                    email: document.getElementById('signin-email').value.trim(),
                    password: document.getElementById('signin-password').value
                };
            }

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
                    const msg = typeof data?.detail === 'string' ? data.detail : (data?.detail?.message || 'Authentication failed');
                    showNotification('Error', msg, 'error');
                    return;
                }
                if (isSignup) {
                    showNotification('Success!', 'Account created. Please sign in.', 'success');
                    setTimeout(() => window.location.reload(), 800);
                } else {
                    showNotification('Success!', 'Signed in successfully', 'success');
                    if (data.access_token) {
                        localStorage.setItem('ccp_token', data.access_token);
                    }
                    setTimeout(() => window.location.href = 'dashboard.html', 800);
                }
            } catch (err) {
                removeLoadingState(submitButton);
                if (authOverlay) authOverlay.classList.remove('active');
                showNotification('Error', 'Network error: ' + err.message, 'error');
            }
        });
    }
    // Remove dev admin shortcut in production
    const devBtn = document.getElementById('dev-admin-btn');
    if (devBtn) {
        devBtn.style.display = 'none';
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
    
    // File upload functionality (multi-file)
    let processedReceipts = [];
    const uploadProgress = document.getElementById('upload-progress');
    const uploadProgressText = document.getElementById('upload-progress-text');
    let exportCsvBtn = null;

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
                handleMultipleFileUpload(files);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleMultipleFileUpload(e.target.files);
            }
        });
    }

    // Export to CSV button handler
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', function() {
            if (processedReceipts.length > 0) {
                generateAndDownloadBatchCSV(processedReceipts);
            }
        });
    }

    // Multi-file upload handler
    async function handleMultipleFileUpload(fileList) {
        // AUTHENTICATION DISABLED FOR DEVELOPMENT
        // const token = localStorage.getItem('ccp_token');
        // if (!token) {
        //     alert('You are not logged in. Please log in to upload files.');
        //     return;
        // }
        processedReceipts = [];
        if (uploadProgress) uploadProgress.style.display = '';
        // Remove export button if present
        if (exportCsvBtn && exportCsvBtn.parentNode) {
            exportCsvBtn.parentNode.removeChild(exportCsvBtn);
            exportCsvBtn = null;
        }
        if (uploadProgressText) uploadProgressText.textContent = 'Uploading...';

        showStep('processing');
        updateProgressStep(2);

        const files = Array.from(fileList);
        let processedCount = 0;
        for (let i = 0; i < files.length; i++) {
            if (uploadProgressText) uploadProgressText.textContent = `Uploading and processing file ${i+1} of ${files.length}...`;
            try {
                const receipt = await handleFileUpload(files[i], true); // true = batch mode
                if (receipt) processedReceipts.push(receipt);
            } catch (err) {
                console.error('Error processing file:', files[i].name, err);
            }
            processedCount++;
        }

        if (uploadProgressText) uploadProgressText.textContent = `Processed ${processedCount} of ${files.length} files.`;
        if (uploadProgress) uploadProgress.style.display = 'none';
        // Dynamically add Export to CSV button after upload
        if (!exportCsvBtn && processedReceipts.length > 0) {
            exportCsvBtn = document.createElement('button');
            exportCsvBtn.id = 'export-csv-btn';
            exportCsvBtn.className = 'btn-primary';
            exportCsvBtn.textContent = 'Export All to CSV';
            exportCsvBtn.style.marginTop = '2em';
            exportCsvBtn.addEventListener('click', function() {
                if (processedReceipts.length > 0) {
                    generateAndDownloadBatchCSV(processedReceipts);
                }
            });
            // Insert after drop zone
            const dropZone = document.getElementById('drop-zone');
            if (dropZone && dropZone.parentNode) {
                dropZone.parentNode.insertBefore(exportCsvBtn, dropZone.nextSibling);
            }
        }

        // Optionally, show a summary or move to review step for the first file
        if (processedReceipts.length > 0) {
            // Show preview for the first file
            loadReceiptPreview(files[0], processedReceipts[0]);
            setTimeout(() => {
                showStep('review');
                updateProgressStep(3);
                populateReviewFields(processedReceipts[0]);
            }, 1000);
        } else {
            showStep('upload');
            updateProgressStep(1);
        }
    }
    
    // Form submission for review
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const submitButton = this.querySelector('button[type="submit"]');
            addLoadingState(submitButton);
            // Collect review data
            const reviewedData = {
                vendor: (document.getElementById('vendor-name')?.value || '').trim() || 'Unknown Vendor',
                date: document.getElementById('receipt-date')?.value || new Date().toISOString().slice(0,10),
                amount: parseFloat(document.getElementById('total-amount')?.value || '0') || 0,
                category: document.getElementById('expense-category')?.value || 'uncategorized',
                gstin: document.getElementById('gst-number')?.value || '',
                tax_amount: document.getElementById('tax-amount')?.value || ''
            };
            const receiptId = window._ccp_uploaded_receipt?.id || window._ccp_uploaded_receipt?._id;
            if (!receiptId) {
                showNotification('Error', 'No receipt ID found for update', 'error');
                removeLoadingState(submitButton);
                return;
            }
            fetch(`http://localhost:8000/api/v1/receipts/${receiptId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                    // Authorization removed for development
                },
                body: JSON.stringify(reviewedData)
            })
            .then(res => res.json().then(data => ({ ok: res.ok, data })))
            .then(({ ok, data }) => {
                removeLoadingState(submitButton);
                if (!ok) {
                    showNotification('Update Failed', data.detail?.message || 'Error updating receipt', 'error');
                    return;
                }
                showNotification('Receipt Saved', 'Receipt has been reviewed and saved!', 'success');
                
                // Generate and download CSV
                generateAndDownloadCSV(reviewedData, data);
                
                // Redirect to dashboard after a short delay
                setTimeout(() => {
                    window.location.href = 'dashboard.html';
                }, 2000);
            })
            .catch(err => {
                removeLoadingState(submitButton);
                showNotification('Network Error', 'Could not update receipt', 'error');
            });
        });
    }
    
    // File upload handler
    // Single file upload handler (used by batch and single)
    async function handleFileUpload(file, batchMode = false) {
        // AUTHENTICATION DISABLED FOR DEVELOPMENT
        // const token = localStorage.getItem('ccp_token');
        // if (!token) {
        //     alert('You are not logged in. Please log in to upload files.');
        //     return;
        // }

        if (!batchMode) {
            showStep('processing');
            updateProgressStep(2);
            if (uploadProgress) uploadProgress.style.display = '';
            if (uploadProgressText) uploadProgressText.textContent = 'Uploading...';
        }

    const formData = new FormData();
    formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/api/v1/receipts/', {
                method: 'POST',
                headers: {
                    // Authorization removed for development
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
            }

            const result = await response.json();
            console.log('Upload successful:', result);

            if (!batchMode) {
                // Store the receipt data for the review step
                localStorage.setItem('current_receipt', JSON.stringify(result));
                window._ccp_uploaded_receipt = result; // Also store globally for the form handler
                // Show preview with backend data
                loadReceiptPreview(file, result);
                // Move to review step after a brief delay
                setTimeout(() => {
                    showStep('review');
                    updateProgressStep(3);
                    populateReviewFields(result);
                }, 1000);
                if (uploadProgress) uploadProgress.style.display = 'none';
            }
            return result;
        } catch (error) {
            console.error('Error during file upload:', error);
            if (!batchMode) {
                alert(`File upload failed: ${error.message}`);
                // Go back to upload step on error
                showStep('upload');
                updateProgressStep(1);
                if (uploadProgress) uploadProgress.style.display = 'none';
            }
            return null;
        }
    // Generate and download CSV for all processed receipts
    function generateAndDownloadBatchCSV(receipts) {
        if (!receipts || receipts.length === 0) return;
        // Prepare CSV data
        const headers = [
            'Receipt ID', 'Date', 'Vendor Name', 'Total Amount', 'Currency', 'Category', 'GST Number', 'Tax Amount', 'Status', 'Created At', 'Filename'
        ];
        const csvRows = [headers.join(',')];
        receipts.forEach(savedData => {
            const row = [
                savedData.id || 'N/A',
                savedData.date || '',
                savedData.vendor || '',
                savedData.amount || 0,
                savedData.currency || 'INR',
                savedData.category || 'uncategorized',
                savedData.gstin || '',
                savedData.tax_amount || '',
                savedData.status || 'approved',
                savedData.created_at || new Date().toISOString(),
                savedData.filename || ''
            ].map(value => {
                const v = value?.toString() || '';
                return v.includes(',') || v.includes('"') ? `"${v.replace(/"/g, '""')}"` : v;
            });
            csvRows.push(row.join(','));
        });
        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `receipts_batch_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        showNotification('CSV Downloaded', 'All receipt data has been exported to CSV file', 'success');
    }
    }

    // Update loadReceiptPreview to accept backend data if needed
    function loadReceiptPreview(file, backendData) {
        const previewImg = document.getElementById('receipt-preview');
        if (!previewImg) return;
        if (file && file.type && file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = (e) => { previewImg.src = e.target.result; };
            reader.readAsDataURL(file);
        } else {
            previewImg.src = '../public/assets/img/logo.png';
        }
        // Optionally update preview fields with backendData
    }

    // Populate review form fields with extracted data
    function populateReviewFields(receiptData) {
        console.log('Populating form fields with:', receiptData);
        
        // Map to correct field IDs from HTML
        const vendorField = document.getElementById('vendor-name');
        const dateField = document.getElementById('receipt-date');
        const amountField = document.getElementById('total-amount');
        const categoryField = document.getElementById('expense-category');
        const gstinField = document.getElementById('gst-number');
        const taxAmountField = document.getElementById('tax-amount');

        // Clear and populate vendor name
        if (vendorField) {
            const vendor = receiptData.vendor || '';
            // Clean up vendor name (remove special characters from OCR errors)
            const cleanVendor = vendor.replace(/[|'"_\-~]+$/, '').trim();
            vendorField.value = cleanVendor && cleanVendor !== 'a |' ? cleanVendor : '';
            console.log('Set vendor:', cleanVendor);
        }

        // Populate date (convert to YYYY-MM-DD format for date input)
        if (dateField && receiptData.date && receiptData.date !== '1970-01-01') {
            let dateValue = receiptData.date;
            // Convert MM/DD/YYYY to YYYY-MM-DD
            if (dateValue.includes('/')) {
                const parts = dateValue.split('/');
                if (parts.length === 3) {
                    // Handle both MM/DD/YYYY and DD/MM/YYYY
                    if (parts[2].length === 4) {
                        dateValue = `${parts[2]}-${parts[0].padStart(2, '0')}-${parts[1].padStart(2, '0')}`;
                    }
                }
            }
            dateField.value = dateValue;
            console.log('Set date:', dateValue);
        }

        // Populate amount
        if (amountField && receiptData.amount && receiptData.amount > 0) {
            amountField.value = receiptData.amount;
            console.log('Set amount:', receiptData.amount);
        }

        // Set category
        if (categoryField && receiptData.category) {
            categoryField.value = receiptData.category;
            console.log('Set category:', receiptData.category);
        }

        // Populate GSTIN
        if (gstinField) {
            gstinField.value = receiptData.gstin || '';
            if (!receiptData.gstin) {
                gstinField.placeholder = "Not found on receipt";
                gstinField.classList.add('warning');
            }
        }

        // Populate tax amount
        if (taxAmountField && receiptData.tax_amount) {
            taxAmountField.value = receiptData.tax_amount;
            console.log('Set tax amount:', receiptData.tax_amount);
        }

        // Show extracted OCR text for debugging
        console.log('OCR Text:', receiptData.extracted?.ocr_text);
    }

    // Generate and download CSV for the approved receipt
    function generateAndDownloadCSV(reviewedData, savedData) {
        console.log('Generating CSV for:', reviewedData);
        
        // Prepare CSV data
        const csvData = [{
            'Receipt ID': savedData.id || 'N/A',
            'Date': reviewedData.date || savedData.date || '',
            'Vendor Name': reviewedData.vendor || savedData.vendor || '',
            'Total Amount': reviewedData.amount || savedData.amount || 0,
            'Currency': savedData.currency || 'INR',
            'Category': reviewedData.category || savedData.category || 'uncategorized',
            'GST Number': reviewedData.gstin || savedData.gstin || '',
            'Tax Amount': reviewedData.tax_amount || savedData.tax_amount || '',
            'Status': savedData.status || 'approved',
            'Created At': savedData.created_at || new Date().toISOString(),
            'Filename': savedData.filename || ''
        }];

        // Convert to CSV format
        const headers = Object.keys(csvData[0]);
        const csvContent = [
            headers.join(','),
            ...csvData.map(row => 
                headers.map(header => {
                    const value = row[header]?.toString() || '';
                    // Escape quotes and wrap in quotes if contains comma
                    return value.includes(',') || value.includes('"') 
                        ? `"${value.replace(/"/g, '""')}"` 
                        : value;
                }).join(',')
            )
        ].join('\n');

        // Create and download CSV file
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `receipt_${savedData.id || Date.now()}_${new Date().toISOString().slice(0, 10)}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('CSV downloaded successfully');
        showNotification('CSV Downloaded', 'Receipt data has been exported to CSV file', 'success');
    }

    // Prefill review form with backend data
    function prefillReviewForm(data) {
        if (!data) return;
        document.getElementById('vendor-name').value = data.vendor || data.extracted?.vendor || '';
        document.getElementById('receipt-date').value = data.date || data.extracted?.date || '';
        document.getElementById('total-amount').value = data.amount || data.extracted?.amount || '';
        document.getElementById('expense-category').value = data.category || data.extracted?.category || '';
        document.getElementById('gst-number').value = data.gstin || data.extracted?.gstin || '';
        document.getElementById('tax-amount').value = data.tax_amount || data.extracted?.tax_amount || '';
    }
    // ...existing code...
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


// Show/hide upload/review/processing steps
function showStep(step) {
    const uploadStep = document.getElementById('upload-step');
    const processingStep = document.getElementById('processing-step');
    const reviewStep = document.getElementById('review-step');
    if (!uploadStep || !processingStep || !reviewStep) return;
    uploadStep.classList.remove('active');
    processingStep.classList.remove('active');
    reviewStep.classList.remove('active');
    if (step === 'upload') uploadStep.classList.add('active');
    else if (step === 'processing') processingStep.classList.add('active');
    else if (step === 'review') reviewStep.classList.add('active');
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