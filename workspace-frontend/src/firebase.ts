import { getApp, getApps, initializeApp } from "@firebase/app";
import {
  GoogleAuthProvider,
  getAuth,
  signInWithPopup,
  signOut,
} from "@firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

const missingConfig = Object.entries(firebaseConfig)
  .filter(([, value]) => !value?.trim())
  .map(([key]) => key);

export const firebaseConfigurationError = missingConfig.length
  ? `Set ${missingConfig.join(", ")} in workspace-frontend/.env.local to enable Google sign-in.`
  : null;

export const firebaseAuth = firebaseConfigurationError
  ? null
  : getAuth(
      getApps().length
        ? getApp()
        : initializeApp(firebaseConfig),
    );

export async function signInWithGoogle() {
  if (!firebaseAuth) {
    throw new Error(firebaseConfigurationError ?? "Firebase is not configured.");
  }

  const provider = new GoogleAuthProvider();
  provider.setCustomParameters({ prompt: "select_account" });
  return signInWithPopup(firebaseAuth, provider);
}

export async function signOutGoogle() {
  if (firebaseAuth) await signOut(firebaseAuth);
}
