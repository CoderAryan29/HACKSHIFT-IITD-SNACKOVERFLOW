import { useState } from "react";
import type { User } from "@firebase/auth";
import { ArrowLeft, Check, LoaderCircle, LogOut, Sprout, Store } from "lucide-react";
import type { AccountRole } from "./auth-api";
import { firebaseConfigurationError, signInWithGoogle, signOutGoogle } from "./firebase";
import "./account-page.css";

interface AccountPageProps {
  user: User | null;
  profileExists: boolean;
  isLoading: boolean;
  isSavingRole: boolean;
  error: string | null;
  onChooseRole: (role: AccountRole) => Promise<void>;
  onRetryProfile: () => void;
  onBack: () => void;
  onSignedOut: () => void;
}

export default function AccountPage({
  user,
  profileExists,
  isLoading,
  isSavingRole,
  error,
  onChooseRole,
  onRetryProfile,
  onBack,
  onSignedOut,
}: AccountPageProps) {
  const [isSigningIn, setIsSigningIn] = useState(false);
  const [signInError, setSignInError] = useState<string | null>(null);
  const message = signInError ?? error;

  async function handleGoogleSignIn() {
    setIsSigningIn(true);
    setSignInError(null);
    try {
      await signInWithGoogle();
    } catch (caught) {
      setSignInError(
        caught instanceof Error ? caught.message : "Google sign-in could not be completed.",
      );
    } finally {
      setIsSigningIn(false);
    }
  }

  async function handleSignOut() {
    await signOutGoogle();
    onSignedOut();
  }

  return (
    <main className="account-page">
      <div className="account-card">
        <button className="account-back" onClick={onBack}>
          <ArrowLeft size={16} /> Back to landing page
        </button>

        <div className="account-brand">
          <span className="account-brand-icon"><Sprout size={24} /></span>
          <span><strong>KisanSetu</strong><small>Saath Har Kisan Ka</small></span>
        </div>

        {isLoading && !user ? (
          <section className="account-content account-loading" aria-live="polite">
            <LoaderCircle className="account-spinner" size={28} />
            <h1>Checking your sign-in</h1>
            <p>Restoring your Firebase session.</p>
          </section>
        ) : !user ? (
          <section className="account-content">
            <span className="account-eyebrow">YOUR FARM WORKSPACE</span>
            <h1>Sign in to get started</h1>
            <p>Use your Google account to securely access the KisanSetu dashboard and farm assistant.</p>
            {firebaseConfigurationError && (
              <div className="account-notice" role="status">
                Google sign-in needs Firebase web configuration. Add the values shown in
                <code> workspace-frontend/.env.example</code> to
                <code> workspace-frontend/.env.local</code>, then restart Vite.
              </div>
            )}
            {message && <div className="account-error" role="alert">{message}</div>}
            <button
              className="google-sign-in"
              onClick={handleGoogleSignIn}
              disabled={Boolean(firebaseConfigurationError) || isSigningIn}
            >
              {isSigningIn ? <LoaderCircle className="account-spinner" size={18} /> : <GoogleMark />}
              Continue with Google
            </button>
            <p className="account-privacy">Your account is verified by Firebase Authentication.</p>
          </section>
        ) : isLoading ? (
          <section className="account-content account-loading" aria-live="polite">
            <LoaderCircle className="account-spinner" size={28} />
            <h1>Checking your account</h1>
            <p>Connecting your verified Google identity to KisanSetu.</p>
          </section>
        ) : !profileExists ? (
          <section className="account-content">
            <span className="account-eyebrow">ACCOUNT SETUP</span>
            <h1>Welcome{user.displayName ? `, ${user.displayName.split(" ")[0]}` : ""}</h1>
            <p>Choose how you’ll use KisanSetu. You can update your role later in account settings.</p>
            {message && <div className="account-error" role="alert">{message}</div>}
            <div className="account-role-options">
              <button disabled={isSavingRole} onClick={() => void onChooseRole("farmer")}>
                <span className="account-role-icon"><Sprout size={22} /></span>
                <span><strong>Farmer</strong><small>Manage crops, farm tools and marketplace activity</small></span>
                <Check size={17} />
              </button>
              <button disabled={isSavingRole} onClick={() => void onChooseRole("buyer")}>
                <span className="account-role-icon buyer"><Store size={22} /></span>
                <span><strong>Buyer</strong><small>Explore crops and connect with sellers</small></span>
                <Check size={17} />
              </button>
            </div>
            <div className="account-user-row">
              <span>Signed in as {user.email || user.displayName || "Google account"}</span>
              <button onClick={() => void handleSignOut()}><LogOut size={14} /> Sign out</button>
            </div>
            {isSavingRole && <p className="account-saving"><LoaderCircle className="account-spinner" size={16} /> Saving your account…</p>}
            {error && <button className="account-retry" onClick={onRetryProfile}>Retry account check</button>}
          </section>
        ) : (
          <section className="account-content account-loading" aria-live="polite">
            <LoaderCircle className="account-spinner" size={28} />
            <h1>Opening your workspace</h1>
          </section>
        )}
      </div>
    </main>
  );
}

function GoogleMark() {
  return (
    <svg className="google-mark" viewBox="0 0 48 48" aria-hidden="true">
      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5Z" />
      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.93c-.58 2.96-2.26 5.48-4.76 7.18l7.73 6C44.41 38.02 46.98 31.93 46.98 24.55Z" />
      <path fill="#FBBC05" d="M10.53 28.59a14.4 14.4 0 0 1 0-9.18l-7.98-6.19a23.9 23.9 0 0 0 0 21.56l7.98-6.19Z" />
      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.9-5.8l-7.73-6c-2.15 1.45-4.9 2.3-8.17 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48Z" />
    </svg>
  );
}
