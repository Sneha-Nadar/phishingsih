import React from "react";
import "./login.css";

export default function Login({ onRegister }) {
  return (
    <div className="sih-login-root">

      {/* SIH Logo Slot */}
      <div className="sih-logo-container">
        {/* <img src="/sih-logo.png" alt="SIH Logo" /> */}
      </div>

      {/* Login Card */}
      <div className="sih-login-card">
        <h2 className="login-title">Welcome Back 👋</h2>
        <p className="login-sub">Login to continue</p>

        {/* Email */}
        <label className="login-label">Email ID</label>
        <input
          type="email"
          className="login-input"
          placeholder="example@sih.gov.in"
        />

        {/* Password */}
        <label className="login-label">Password</label>
        <input
          type="password"
          className="login-input"
          placeholder="Enter your password"
        />

        {/* Login */}
        <button className="login-btn">
          <a href="/app">Login</a>
        </button>

        <p className="forgot-text">Forgot Password?</p>

        {/* Divider */}
        <div className="sih-divider">
          <span>Or Login With</span>
        </div>

        {/* Google Login */}
        <button className="google-btn">Google Login</button>

        {/* REGISTER OPTION */}
        <div className="register-section">
          <p className="register-text">
            Don’t have an account?{" "}
            <span className="register-link" onClick={onRegister}>
              Register
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
