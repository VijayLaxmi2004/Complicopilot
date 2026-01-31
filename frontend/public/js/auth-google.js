import { getAuth, signInWithPopup, GoogleAuthProvider, createUserWithEmailAndPassword, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-auth.js";
import { app } from "./firebase.js";

const auth = getAuth(app);
console.log("Firebase Auth initialized:", auth);
console.log("Firebase app config:", auth.app.options);

window.addEventListener("DOMContentLoaded", () => {
  console.log("Auth Google script loaded");
  console.log("Current location:", window.location.href);
  console.log("Auth domain from config:", auth.app.options.authDomain);
  
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
      console.log("Event target:", e.target);
      console.log("Default prevented:", e.defaultPrevented);
      
      try {
        // Show loading state
        googleBtn.disabled = true;
        googleBtn.textContent = "Signing in...";
        console.log("Button disabled and text changed");
        
        // Wait a moment to ensure we're not conflicting with other handlers
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const provider = new GoogleAuthProvider();
        console.log("GoogleAuthProvider created:", provider);
        
        // Add some basic scopes
        provider.addScope('email');
        provider.addScope('profile');
        console.log("Scopes added to provider");
        
        console.log("🚀 Starting Firebase signInWithPopup...");
        console.log("Auth object:", auth);
        console.log("Provider object:", provider);
        
        const result = await signInWithPopup(auth, provider);
        console.log("🎉 Sign-in popup completed successfully!");
        console.log("Full result:", result);
        
        const user = result.user;
        console.log("User object:", user);
        console.log("Google sign-in successful:", {
          email: user.email,
          name: user.displayName,
          uid: user.uid,
          photoURL: user.photoURL
        });
        
        const idToken = await user.getIdToken();
        console.log("ID token obtained (length):", idToken.length);
        
        localStorage.setItem('ccp_token', idToken);
        localStorage.setItem('ccp_user_email', user.email || '');
        localStorage.setItem('ccp_user_name', user.displayName || '');
        localStorage.setItem('ccp_user_photo', user.photoURL || '');
        localStorage.setItem('ccp_user_uid', user.uid || '');
        console.log("Data saved to localStorage");
        
        // Show success message
        console.log("✅ Authentication successful! Redirecting to dashboard...");
        alert("Successfully signed in with Google!");
        
        // Redirect to dashboard
        window.location.href = 'dashboard.html';
        
      } catch (error) {
        console.error("❌ Firebase Google sign-in error:");
        console.error("Error code:", error.code);
        console.error("Error message:", error.message);
        console.error("Full error object:", error);
        console.error("Error stack:", error.stack);
        
        let errorMessage = `Firebase Auth failed: ${error.message}`;
        
        // Handle Firebase-specific error codes
        if (error.code === 'auth/popup-blocked') {
          errorMessage = "Popup was blocked. Please allow popups and try again.";
          console.log("💡 Try: Allow popups in browser settings");
        } else if (error.code === 'auth/popup-closed-by-user') {
          errorMessage = "Sign-in was cancelled.";
          console.log("💡 User closed the popup");
        } else if (error.code === 'auth/unauthorized-domain') {
          errorMessage = "Domain not authorized in Firebase Console. Please add localhost.";
          console.log("💡 Add localhost to Firebase Console authorized domains");
        } else if (error.code === 'auth/operation-not-allowed') {
          errorMessage = "Google sign-in not enabled in Firebase Console.";
          console.log("💡 Enable Google sign-in in Firebase Console");
        } else if (error.code === 'auth/invalid-api-key') {
          errorMessage = "Invalid Firebase API key.";
          console.log("💡 Check Firebase config API key");
        }
        
        console.error("Showing error to user:", errorMessage);
        alert(errorMessage);
        
        // Reset button state
        googleBtn.disabled = false;
        googleBtn.innerHTML = '<span class="social-icon">G</span>Google';
        console.log("Button state reset");
      }
    }, true); // Use capture phase to get the event first
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
