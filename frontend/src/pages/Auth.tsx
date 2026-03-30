import axios from "axios";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

const base_url = "http://localhost:8000";

type AuthStatus = "idle" | "loading" | "done" | "error";
type AuthMode = "login" | "signup";

export default function Auth() {
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [status, setStatus] = useState<AuthStatus>("idle");
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  const passwordMismatch = mode === "signup" && confirm.length > 0 && password !== confirm;

  const switchMode = (next: AuthMode) => {
    setMode(next);
    setEmail("");
    setPassword("");
    setConfirm("");
    setStatus("idle");
    setErrorMsg("");
  };

  const handleSubmit = async () => {
    if (!email || !password) return;
    if (mode === "signup" && (!confirm || passwordMismatch)) return;
    setStatus("loading");
    setErrorMsg("");
    try {
      if (mode === "login") {
        await axios.post(base_url + "/login", { email, password },{withCredentials:true});
        navigate("/home");
      } else {
        await axios.post(base_url + "/signup", { email, password });
        setStatus("done");
        return;
      }
    } catch (err: any) {
      setStatus("error");
      setErrorMsg(err?.response?.data?.detail ?? "Something went wrong. Please try again.");
    }
    setStatus("idle");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSubmit();
  };

  return (
    <>
      <style>{`
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeSwap {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      <div className="flex h-screen bg-zinc-950 items-center justify-center p-6">
        <div
          className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8 shadow-2xl"
          style={{ animation: "slideIn 0.25s ease-out both" }}
        >
          {/* Header */}
          <div className="mb-8">
            <span className="text-xs font-semibold tracking-widest text-cyan-400 uppercase">
              S3 Multipart
            </span>
            <h1 className="mt-1 text-2xl font-bold text-white tracking-tight">
              {mode === "login" ? "Sign in" : "Create account"}
            </h1>
            <p className="mt-1 text-sm text-zinc-500">
              {mode === "login"
                ? "Enter your credentials to continue"
                : "Get started — it only takes a moment"}
            </p>
          </div>

          {/* Success state (signup only) */}
          {status === "done" ? (
            <div className="py-6 text-center" style={{ animation: "fadeSwap 0.2s ease-out both" }}>
              <div className="w-10 h-10 rounded-full bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mx-auto mb-3">
                <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm font-semibold text-white">Account created!</p>
              <p className="text-xs text-zinc-500 mt-1">You can now sign in.</p>
              <button
                onClick={() => switchMode("login")}
                className="mt-4 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
              >
                Go to sign in →
              </button>
            </div>
          ) : (
            <div style={{ animation: "fadeSwap 0.2s ease-out both" }} key={mode}>
              {/* Fields */}
              <div className="space-y-3 mb-4">
                <div>
                  <label className="block text-xs font-semibold text-zinc-500 mb-1.5 tracking-wide uppercase">
                    Email
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="you@example.com"
                    disabled={status === "loading"}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600
                      focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/40
                      disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-150"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-zinc-500 mb-1.5 tracking-wide uppercase">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="••••••••"
                    disabled={status === "loading"}
                    className="w-full bg-zinc-800 border border-zinc-700 rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600
                      focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500/40
                      disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-150"
                  />
                </div>

                {mode === "signup" && (
                  <div>
                    <label className="block text-xs font-semibold text-zinc-500 mb-1.5 tracking-wide uppercase">
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      value={confirm}
                      onChange={(e) => setConfirm(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="••••••••"
                      disabled={status === "loading"}
                      className={`w-full bg-zinc-800 border rounded-xl px-4 py-3 text-sm text-white placeholder-zinc-600
                        focus:outline-none focus:ring-1
                        disabled:opacity-40 disabled:cursor-not-allowed transition-colors duration-150
                        ${passwordMismatch
                          ? "border-red-500/60 focus:border-red-500 focus:ring-red-500/40"
                          : "border-zinc-700 focus:border-cyan-500 focus:ring-cyan-500/40"
                        }`}
                    />
                    {passwordMismatch && (
                      <p className="text-xs text-red-400 mt-1.5">Passwords don't match</p>
                    )}
                  </div>
                )}
              </div>

              {/* Error */}
              {status === "error" && (
                <p className="text-xs text-red-400 mb-4">{errorMsg}</p>
              )}

              {/* Submit */}
              <button
                onClick={handleSubmit}
                disabled={
                  !email || !password ||
                  (mode === "signup" && (!confirm || passwordMismatch)) ||
                  status === "loading"
                }
                className="w-full py-3 px-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 active:scale-95
                  disabled:opacity-30 disabled:cursor-not-allowed
                  transition-all duration-150 text-zinc-950 text-sm font-bold tracking-wide"
              >
                {status === "loading"
                  ? mode === "login" ? "Signing in…" : "Creating account…"
                  : mode === "login" ? "Sign in" : "Create account"}
              </button>

              {/* Mode toggle */}
              <p className="text-center text-xs text-zinc-600 mt-4">
                {mode === "login" ? "Don't have an account? " : "Already have an account? "}
                <button
                  onClick={() => switchMode(mode === "login" ? "signup" : "login")}
                  className="text-zinc-400 hover:text-white transition-colors"
                >
                  {mode === "login" ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>
          )}
        </div>
      </div>
    </>
  );
}