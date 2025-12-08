import React from "react";
import "./register.css";

export default function Register() {
  return (
    <div className="sih-register-root">

      {/* SIH Logo Slot */}
      <div className="sih-logo-container">
        {/* <img src="/sih-logo.png" alt="SIH Logo" /> */}
      </div>

      {/* Register Card */}
      <div className="sih-register-card">

        <h2 className="register-title">Create Account 👤</h2>
        <p className="register-sub">Join the SIH platform and get started</p>

        {/* Full Name */}
        <label className="register-label">Full Name</label>
        <input
          type="text"
          className="register-input"
          placeholder="Enter your full name"
        />

        {/* Email */}
        <label className="register-label">Email ID</label>
        <input
          type="email"
          className="register-input"
          placeholder="example@sih.gov.in"
        />

        {/* Password */}
        <label className="register-label">Password</label>
        <input
          type="password"
          className="register-input"
          placeholder="Create a password"
        />

        {/* Confirm Password */}
        <label className="register-label">Confirm Password</label>
        <input
          type="password"
          className="register-input"
          placeholder="Re-enter your password"
        />

        {/* Register Button */}
        <button className="register-btn">Register</button>

        {/* Divider */}
        <div className="sih-divider">
          <span>Or Register With</span>
        </div>

        {/* Google Button */}
        <button className="google-btn">Google Signup</button>

        {/* Login Option */}
        <div className="login-section">
          <p className="login-text">
            Already have an account?{" "}
            <span className="login-link">Login</span>
          </p>
        </div>

      </div>
    </div>
  );
}
