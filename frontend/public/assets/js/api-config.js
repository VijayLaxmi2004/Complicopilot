// API Configuration for CompliCopilot
// Automatically detects environment and sets appropriate API base URL

(function() {
    'use strict';
    
    // Determine API base URL based on environment
    function getApiBaseUrl() {
        const hostname = window.location.hostname;
        
        // Production - Firebase Hosting (update this URL after deploying backend)
        if (hostname.includes('complicopilot.web.app') || 
            hostname.includes('complicopilot.firebaseapp.com')) {
            // TODO: Replace with your deployed backend URL (Render, Railway, Cloud Run, etc.)
            return 'https://complicopilot-backend.onrender.com';
        }
        
        // Local development with Docker
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            const port = window.location.port;
            // If frontend is on port 3000 (Docker), backend is on 8000
            if (port === '3000') {
                return 'http://localhost:8000';
            }
            // If frontend is on port 5500 (Live Server) or 8080, backend is on 8080
            if (port === '5500' || port === '8080') {
                return 'http://localhost:8080';
            }
            // Default to port 8000
            return 'http://localhost:8000';
        }
        
        // Mobile/LAN development
        if (hostname.match(/^192\.168\./)) {
            return `http://${hostname}:8000`;
        }
        
        // Default fallback - relative URLs
        return '';
    }
    
    // Export configuration globally
    window.API_CONFIG = {
        BASE_URL: getApiBaseUrl(),
        
        // Helper to build full API URLs
        url: function(path) {
            // Ensure path starts with /
            if (!path.startsWith('/')) {
                path = '/' + path;
            }
            return this.BASE_URL + path;
        },
        
        // Endpoints
        endpoints: {
            receipts: '/api/v1/receipts/',
            receiptsBatch: '/api/v1/receipts/batch',
            receipt: (id) => `/api/v1/receipts/${id}`,
            auth: {
                signup: '/auth/signup',
                signin: '/auth/signin',
                googleLogin: '/auth/google/login'
            },
            health: '/api/health'
        }
    };
    
    console.log('[API Config] Environment:', window.location.hostname);
    console.log('[API Config] Base URL:', window.API_CONFIG.BASE_URL || '(relative)');
})();
