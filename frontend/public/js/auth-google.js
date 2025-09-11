import { getAuth, signInWithPopup, GoogleAuthProvider } from "../node_modules/firebase/auth";
import { app } from "./firebase.js";

window.addEventListener("DOMContentLoaded", () => {
  const googleBtn = document.querySelector(".btn-social.google");
  if (googleBtn) {
    googleBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      const auth = getAuth(app);
      const provider = new GoogleAuthProvider();
      try {
        const result = await signInWithPopup(auth, provider);
        // User info
        const user = result.user;
        // You can send user info or ID token to your backend here
        alert(`Signed in as: ${user.displayName} (${user.email})`);
        // Redirect or update UI as needed
      } catch (error) {
        alert("Google sign-in failed: " + error.message);
      }
    });
  }
});
