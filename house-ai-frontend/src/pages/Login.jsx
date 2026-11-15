import { useState } from "react";
import { login, signup } from "../api";

export default function Login({ onLogin }) {
  const [isSignup, setIsSignup] = useState(false); // false = log in, true = sign up
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault(); // stop the page from reloading
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const user = isSignup
        ? await signup(name, email, password)
        : await login(email, password);
      onLogin(user); // App now knows who's logged in and shows the home page
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <header className="hero">
        <span className="eyebrow">Household AI Assistant</span>
        <h1 className="hero-title">
          {isSignup ? "Create your" : "Welcome"}
          <br />
          {isSignup ? "account." : "Back."}
        </h1>
      </header>

      <section className="switchboard">
        <form className="auth-card" onSubmit={handleSubmit}>
          {isSignup && (
            <input
              className="auth-input"
              type="text"
              placeholder="Your name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          )}
          <input
            className="auth-input"
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            className="auth-input"
            type="password"
            placeholder="Password (at least 6 characters)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="query-submit auth-submit" type="submit" disabled={isLoading}>
            {isLoading ? "Please wait…" : isSignup ? "Sign up" : "Log in"}
          </button>

          <p className="auth-switch">
            {isSignup ? "Already have an account?" : "New here?"}{" "}
            <button
              type="button"
              className="link-button"
              onClick={() => {
                setIsSignup(!isSignup);
                setErrorMsg(null);
              }}
            >
              {isSignup ? "Log in" : "Create an account"}
            </button>
          </p>
        </form>
      </section>
    </>
  );
}
