import { getAuth, signInWithPopup, signInWithRedirect, getRedirectResult, GoogleAuthProvider, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { app } from "./firebase.js";

const auth = getAuth(app);
console.log("Firebase Auth initialized:", auth);
console.log("Firebase app config:", auth.app.options);

// Detect if we're on mobile or accessing via IP (not localhost)
function shouldUseRedirect() {
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
  const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
  const isIPAddress = /^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(window.location.hostname);

  console.log("Auth detection:", { isMobile, isLocalhost, isIPAddress, hostname: window.location.hostname });

  // Use redirect for mobile or when accessing via IP address
  return isMobile || isIPAddress;
}

window.addEventListener("DOMContentLoaded", async () => {
  console.log("Auth Google script loaded");
  console.log("Current location:", window.location.href);
  console.log("Auth domain from config:", auth.app.options.authDomain);

  // Check for redirect result (if coming back from Google sign-in)
  try {
    const result = await getRedirectResult(auth);
    if (result) {
      console.log("🎉 Redirect sign-in successful!");
      const user = result.user;
      const idToken = await user.getIdToken();

      localStorage.setItem('ccp_token', idToken);
      localStorage.setItem('ccp_user_email', user.email || '');
      localStorage.setItem('ccp_user_name', user.displayName || '');
      localStorage.setItem('ccp_user_photo', user.photoURL || '');
      localStorage.setItem('ccp_user_uid', user.uid || '');

      console.log("✅ User authenticated via redirect:", user.email);
      window.location.href = 'dashboard.html';
      return;
    }
  } catch (error) {
    console.error("Redirect result error:", error);
  }
  
  // Test Firebase connection
  console.log("Testing Firebase connection...");
  console.log("Auth current user:", auth.currentUser);
  
  // Google Sign-in
  const googleBtn = document.querySelector(".btn-social.google");
  console.log("Looking for Google button...");
  console.log("Google button element:", googleBtn);
  
  if (googleBtn) {
    console.log("✅ Google button found, adding click listener");
    
    // Remove any existing event listeners and prevent default behavior
    googleBtn.onclick = null;
    googleBtn.removeAttribute('onclick');
    
    googleBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();

      console.log("🔥 Google sign-in button clicked!");
      const useRedirect = shouldUseRedirect();
      console.log("Using redirect method:", useRedirect);

      try {
        // Show loading state
        googleBtn.disabled = true;
        googleBtn.textContent = useRedirect ? "Redirecting..." : "Signing in...";

        const provider = new GoogleAuthProvider();
        provider.addScope('email');
        provider.addScope('profile');

        if (useRedirect) {
          // Use redirect for mobile/IP access - works better across devices
          console.log("🚀 Starting Firebase signInWithRedirect...");
          await signInWithRedirect(auth, provider);
          // Page will redirect to Google, then back here
          // getRedirectResult() at page load will handle the result
        } else {
          // Use popup for desktop localhost
          console.log("🚀 Starting Firebase signInWithPopup...");
          const result = await signInWithPopup(auth, provider);
          console.log("🎉 Sign-in popup completed successfully!");

          const user = result.user;
          console.log("Google sign-in successful:", user.email);

          const idToken = await user.getIdToken();
          localStorage.setItem('ccp_token', idToken);
          localStorage.setItem('ccp_user_email', user.email || '');
          localStorage.setItem('ccp_user_name', user.displayName || '');
          localStorage.setItem('ccp_user_photo', user.photoURL || '');
          localStorage.setItem('ccp_user_uid', user.uid || '');

          console.log("✅ Authentication successful! Redirecting to dashboard...");
          window.location.href = 'dashboard.html';
        }

      } catch (error) {
        console.error("❌ Firebase Google sign-in error:");
        console.error("Error code:", error.code);
        console.error("Error message:", error.message);

        let errorMessage = `Sign-in failed: ${error.message}`;

        if (error.code === 'auth/popup-blocked') {
          errorMessage = "Popup was blocked. Trying redirect method...";
          // Fallback to redirect
          try {
            const provider = new GoogleAuthProvider();
            provider.addScope('email');
            provider.addScope('profile');
            await signInWithRedirect(auth, provider);
            return;
          } catch (redirectError) {
            errorMessage = "Sign-in failed. Please try again.";
          }
        } else if (error.code === 'auth/popup-closed-by-user') {
          errorMessage = "Sign-in was cancelled.";
        } else if (error.code === 'auth/unauthorized-domain') {
          errorMessage = "This domain is not authorized. Please add " + window.location.hostname + " to Firebase Console → Authentication → Settings → Authorized domains";
          console.log("💡 Add this domain to Firebase:", window.location.hostname);
        } else if (error.code === 'auth/operation-not-allowed') {
          errorMessage = "Google sign-in not enabled in Firebase Console.";
        }

        alert(errorMessage);

        // Reset button state
        googleBtn.disabled = false;
        googleBtn.innerHTML = '<span class="social-icon">G</span>Google';
      }
    }, true);
  } else {
    console.error("❌ Google button NOT found!");
    console.log("Available buttons:", document.querySelectorAll('button'));
    console.log("Available elements with .btn-social:", document.querySelectorAll('.btn-social'));
    console.log("Available elements with .google:", document.querySelectorAll('.google'));
  }
  
  // Email/Password Sign-up
  const signupForm = document.getElementById('signup-form');
  if (signupForm) {
    const form = signupForm.closest('form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const email = formData.get('email');
        const password = formData.get('password');
        const confirmPassword = formData.get('confirm_password');
        const name = formData.get('name');
        
        if (password !== confirmPassword) {
          alert('Passwords do not match');
          return;
        }
        
        try {
          const submitBtn = form.querySelector('button[type="submit"]');
          submitBtn.disabled = true;
          submitBtn.textContent = 'Creating account...';
          
          const userCredential = await createUserWithEmailAndPassword(auth, email, password);
          const user = userCredential.user;
          
          const idToken = await user.getIdToken();
          localStorage.setItem('ccp_token', idToken);
          localStorage.setItem('ccp_user_email', email);
          localStorage.setItem('ccp_user_name', name || '');
          localStorage.setItem('ccp_user_photo', user.photoURL || '');
          localStorage.setItem('ccp_user_uid', user.uid || '');
          
          alert('Account created successfully!');
          window.location.href = 'dashboard.html';
          
        } catch (error) {
          console.error('Sign-up error:', error);
          alert(`Sign-up failed: ${error.message}`);
          
          const submitBtn = form.querySelector('button[type="submit"]');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Create Account';
        }
      });
    }
  }
  
  // Email/Password Sign-in
  const signinForm = document.getElementById('signin-form');
  if (signinForm) {
    const form = signinForm.closest('form');
    if (form) {
      form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const email = formData.get('email');
        const password = formData.get('password');
        
        try {
          const submitBtn = form.querySelector('button[type="submit"]');
          submitBtn.disabled = true;
          submitBtn.textContent = 'Signing in...';
          
          const userCredential = await signInWithEmailAndPassword(auth, email, password);
          const user = userCredential.user;
          
          const idToken = await user.getIdToken();
          localStorage.setItem('ccp_token', idToken);
          localStorage.setItem('ccp_user_email', email);
          localStorage.setItem('ccp_user_name', user.displayName || '');
          localStorage.setItem('ccp_user_photo', user.photoURL || '');
          localStorage.setItem('ccp_user_uid', user.uid || '');
          
          alert('Signed in successfully!');
          window.location.href = 'dashboard.html';
          
        } catch (error) {
          console.error('Sign-in error:', error);
          alert(`Sign-in failed: ${error.message}`);
          
          const submitBtn = form.querySelector('button[type="submit"]');
          submitBtn.disabled = false;
          submitBtn.textContent = 'Sign In';
        }
      });
    }
  }
});
