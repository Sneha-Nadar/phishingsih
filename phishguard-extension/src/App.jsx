import React, { useState } from "react";
import "./popup.css";

const BACKEND_URL = "http://127.0.0.1:8000";

export default function App() {
  const [mode, setMode] = useState("url");
  const [url, setUrl] = useState("");
  const [imageName, setImageName] = useState("");
  const [textBody, setTextBody] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // ------------------------------------------------------
  // RESULT BUILDER
  // ------------------------------------------------------
  const buildResultFromResponse = (sourceLabel, data) => {
    return {
      score: data.score ?? data.final_risk_score ?? 0,
      status: data.verdict?.toLowerCase() ?? "safe",
      source: sourceLabel,
      raw: data,
    };
  };

  // ------------------------------------------------------
  // URL SCAN
  // ------------------------------------------------------
  const handleUrlScan = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("url", url);

      const res = await fetch(`${BACKEND_URL}/analyze/url`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      setResult(buildResultFromResponse("URL", data));
    } catch (err) {
      console.error(err);
      setError("Backend unreachable. Start FastAPI server.");
    }

    setLoading(false);
  };

  // ------------------------------------------------------
  // TEXT SCAN
  // ------------------------------------------------------
  const handleTextScan = async () => {
    if (!textBody.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("body", textBody);

      const res = await fetch(`${BACKEND_URL}/analyze/text`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      setResult(buildResultFromResponse("Text", data));
    } catch (err) {
      console.error(err);
      setError("Cannot reach backend.");
    }

    setLoading(false);
  };

  // ------------------------------------------------------
  // IMAGE SCAN
  // ------------------------------------------------------
  const handleImageChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setImageName(file.name);
    setLoading(true);
    setError("");
    setResult(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch(`${BACKEND_URL}/analyze/image`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();
      setResult(buildResultFromResponse("Image", data));
    } catch (err) {
      console.error(err);
      setError("Image scan failed.");
    }

    setLoading(false);
  };

  // Status color
  const activeStatus = result?.status;
  const scoreClass =
    activeStatus === "safe" ? "score-safe" : "score-phishing";

  return (
    <>
      {/* BACKGROUND SCROLL TEXT */}
      <div className="sih-scroll-text">
        PHISHBUSTERZ • SMART INDIA HACKATHON 2025 • CYBERSECURITY •
      </div>

      {/* OTHER BACKGROUND LAYERS */}
      <div className="india-bg"></div>
      <div className="saffron-glow"></div>
      <div className="green-glow"></div>
      <div className="cyber-grid"></div>
      <div className="sih-glow-saffron"></div>
      <div className="sih-glow-green"></div>
      <div className="ashoka-holo"></div>

      <div className="sih-root">
        <div className="sih-shell">

          {/* HEADER */}
          <header className="sih-header">
            <div className="sih-logo-circle">PB</div>
            <div className="sih-heading-block">
              <p className="sih-tag">SMART INDIA HACKATHON 2025</p>
              <h1 className="sih-title">PhishBusterz</h1>
              <p className="sih-sub">Image, URL & text based phishing detection system.</p>
            </div>
          </header>

          {/* MODE SWITCH */}
          <div className="sih-mode-switch">
            <button
              className={`sih-mode-btn ${mode === "url" ? "active-mode" : ""}`}
              onClick={() => {
                setMode("url");
                setResult(null);
              }}
            >
              URL Scan
            </button>

            <button
              className={`sih-mode-btn ${mode === "image" ? "active-mode" : ""}`}
              onClick={() => {
                setMode("image");
                setResult(null);
              }}
            >
              Image Scan
            </button>

            <button
              className={`sih-mode-btn ${mode === "text" ? "active-mode" : ""}`}
              onClick={() => {
                setMode("text");
                setResult(null);
              }}
            >
              Text Scan
            </button>
          </div>

          {/* URL INPUT */}
          {mode === "url" && (
            <section className="sih-section">
              <h2 className="sih-section-title">Check <span>URL</span></h2>

              <input
                className="sih-input"
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />

              <button className="sih-btn-green full" onClick={handleUrlScan}>
                Analyze URL
              </button>
            </section>
          )}

          {/* IMAGE INPUT */}
          {mode === "image" && (
            <section className="sih-section">
              <h2 className="sih-section-title">Scan <span>Screenshot</span></h2>

              <div
                className="sih-upload-box"
                role="button"
                onClick={() => document.getElementById("sih-image-input").click()}
              >
                <p className="sih-upload-main">Click to upload a phishing screenshot</p>
                <p className="sih-upload-sub">PNG / JPG • Login pages • Fake emails</p>
                {imageName && <p className="sih-file-name">{imageName}</p>}
              </div>

              <input
                id="sih-image-input"
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={handleImageChange}
              />
            </section>
          )}

          {/* TEXT INPUT */}
          {mode === "text" && (
            <section className="sih-section">
              <h2 className="sih-section-title">Scan <span>Text / Email</span></h2>

              <textarea
                className="sih-textarea"
                placeholder="Paste email body, SMS, WhatsApp message..."
                value={textBody}
                onChange={(e) => setTextBody(e.target.value)}
                rows={4}
              />

              <button className="sih-btn-green full" onClick={handleTextScan}>
                Analyze Text
              </button>
            </section>
          )}

          {/* RESULTS */}
          <section className="sih-result-area">
            {error && (
              <div className="sih-result-box" style={{ color: "red" }}>
                {error}
              </div>
            )}

            {loading && (
              <div className="sih-result-box">
                <div className="loader-sih"></div>
                <p>Analyzing...</p>
              </div>
            )}

            {!loading && result && (
              <div className="sih-result-box">
                <h3 className="result-title">
                  {result.source} • {result.status === "safe" ? "Legitimate" : "Phishing Likely"}
                </h3>

                <div
                  className={`score-circle ${scoreClass} mb-3`}
                  style={{ "--score": result.score }}
                >
                  <span>{result.score}</span>
                </div>

                <p className="result-desc">
                  {result.status === "safe"
                    ? "Looks safe based on current checks."
                    : "Strong phishing signals detected. Do NOT continue."}
                </p>
              </div>
            )}
          </section>

        </div>
      </div>
    </>
  );
}
