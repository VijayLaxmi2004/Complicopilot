// frontend/public/js/firebase.js
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBL8_6nVU2OCwvNRYWqbx4NzD3PgftnFUE",
  authDomain: "complicopilot.vercel.app",
  // If deploying to Vercel, you may also want to add:
  // authDomain: ["complicopilot-864.firebaseapp.com", "complicopilot.vercel.app"],
  projectId: "complicopilot",
  storageBucket: "complicopilot.firebasestorage.app",
  messagingSenderId: "314466368999",
  appId: "1:314466368999:web:90bddd39193c34fc80d142",
  measurementId: "G-8657BX50YD"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export { app, analytics };
