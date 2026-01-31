// Firebase initialization (CDN modules so no bundler needed)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.0/firebase-analytics.js";

// IMPORTANT: Ensure these values match your real Firebase project.
// Using the correct Firebase project configuration
const firebaseConfig = {
  apiKey: "AIzaSyBL8_6nVU2OCwvNRYWqbx4NzD3PgftnFUE",
  authDomain: "complicopilot.firebaseapp.com",
  projectId: "complicopilot",
  storageBucket: "complicopilot.appspot.com",
  messagingSenderId: "314466368999",
  appId: "1:314466368999:web:90bddd39193c34fc80d142",
  measurementId: "G-8657BX50YD"
};

console.log("Firebase config:", firebaseConfig);
const app = initializeApp(firebaseConfig);
let analytics = null;
// Skip analytics on localhost to avoid 403 errors during development
if (typeof window !== "undefined" && 'measurementId' in firebaseConfig && location.hostname !== "localhost") {
  try { analytics = getAnalytics(app); } catch (e) { 
    console.warn("Analytics initialization skipped:", e.message); 
  }
} else {
  console.info("Skipping Firebase Analytics (development environment or no measurementId)");
}

export { app, analytics };
