import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
// Only load analytics outside localhost (avoid 403 noise if misconfigured)
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
  apiKey: "AIzaSyBL8_6nVU2OCwvNRYWqbx4NzD3PgftnFUE",
  authDomain: "complicopilot.firebaseapp.com",
  projectId: "complicopilot",
  storageBucket: "complicopilot.appspot.com",
  messagingSenderId: "314466368999",
  appId: "1:314466368999:web:90bddd39193c34fc80d142",
  measurementId: "G-8657BX50YD"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);

if (firebaseConfig.measurementId && location.hostname !== "localhost") {
  try { getAnalytics(app); } catch(e){ console.warn("Analytics skipped", e); }
} else {
  console.info("Skipping Analytics in dev.");
}