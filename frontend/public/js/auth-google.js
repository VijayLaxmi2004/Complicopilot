import { getAuth, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
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
        const user = result.user;
        alert(`Signed in as: ${user.displayName} (${user.email})`);
      } catch (error) {
        alert("Google sign-in failed: " + error.message);
      }
    });
  }
});
