import React, { useState } from "react";
import "./popup.css";

const BACKEND_URL = "http://127.0.0.1:8000";

export default function App() {
  const [mode, setMode] = useState("url");
  const [url, setUrl] = useState("");
  const [imageName, setImageName] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [textBody, setTextBody] = useState("");

  const [result, setResult] = useState(null);           // Normal scan output
  const [fullImageResult, setFullImageResult] = useState(null); // Deep scan output

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // --------------------------- COMMON RESULT BUILDER ---------------------------
  const buildResultFromResponse = (sourceLabel, data) => {
    return {
      score: data.score ?? data.final_risk_score ?? 0,
      status: data.verdict?.toLowerCase() ?? "safe",
      source: sourceLabel,
      raw: data,
    };
  };

  // --------------------------- URL SCAN ---------------------------
  const handleUrlScan = async () => {
    if (!url.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);
    setFullImageResult(null);

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

  // --------------------------- TEXT SCAN ---------------------------
  const handleTextScan = async () => {
    if (!textBody.trim()) return;

    setLoading(true);
    setError("");
    setResult(null);
    setFullImageResult(null);

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

  // --------------------------- BASIC IMAGE SCAN ---------------------------
  const handleImageScan = async () => {
    if (!selectedFile) {
      setError("Please upload an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setFullImageResult(null);

    try {
      const form = new FormData();
      form.append("file", selectedFile);

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

  // ---------------------- FULL IMAGE (OCR + YOLO + STEGO) ----------------------
  const handleFullImageScan = async () => {
    if (!selectedFile) {
      setError("Upload an image first");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);
    setFullImageResult(null);

    try {
      const form = new FormData();
      form.append("file", selectedFile);

      const res = await fetch(`${BACKEND_URL}/analyze/image/full`, {
        method: "POST",
        body: form,
      });

      const data = await res.json();

      setFullImageResult({
        stego: data?.stego_analysis ?? null,
        yolo: data?.yolo ?? null,
        ocr: data?.ocr_text ?? null,
        mobilenet: data?.mobilenet ?? null,
      });
    } catch (err) {
      console.error(err);
      setError("Full image scan failed.");
    }

    setLoading(false);
  };

  // --------------------------- UI ---------------------------

  const activeStatus = result?.status;
  const scoreClass = activeStatus === "safe" ? "score-safe" : "score-phishing";

  return (
    <>
      {/* BACKGROUND EFFECTS */}
      <div className="sih-scroll-text">PHISHBUSTERZ • SMART INDIA HACKATHON 2025 • CYBERSECURITY •</div>
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
              <p className="sih-sub">Image, URL & Text based phishing detection system.</p>
            </div>
          </header>

          {/* MODE SWITCH */}
          <div className="sih-mode-switch">
            <button className={`sih-mode-btn ${mode === "url" ? "active-mode" : ""}`} onClick={() => setMode("url")}>URL Scan</button>
            <button className={`sih-mode-btn ${mode === "image" ? "active-mode" : ""}`} onClick={() => setMode("image")}>Image Scan</button>
            <button className={`sih-mode-btn ${mode === "text" ? "active-mode" : ""}`} onClick={() => setMode("text")}>Text Scan</button>
            <button className={`sih-mode-btn ${mode === "deep" ? "active-mode" : ""}`} onClick={() => setMode("deep")}>
              Deep Stego Scan
            </button>
          </div>

          {/* URL INPUT UI */}
          {mode === "url" && (
            <section className="sih-section">
              <h2 className="sih-section-title">Check <span>URL</span></h2>
              <input className="sih-input" placeholder="https://example.com" value={url} onChange={(e) => setUrl(e.target.value)} />
              <button className="sih-btn-green full" onClick={handleUrlScan}>Analyze URL</button>
            </section>
          )}

          {/* IMAGE UPLOAD + SCAN */}
          {(mode === "image" || mode === "deep") && (
            <section className="sih-section">
              <h2 className="sih-section-title">Upload <span>Screenshot</span></h2>

              <div className="sih-upload-box" onClick={() => document.getElementById("upload-img").click()}>
                <p className="sih-upload-main">Upload suspicious screenshot</p>
                <p className="sih-upload-sub">PNG / JPG • Fake Login Pages • Emails</p>
                {imageName && <p className="sih-file-name">{imageName}</p>}
              </div>

              <input
                id="upload-img"
                type="file"
                accept="image/*"
                style={{ display: "none" }}
                onChange={(e) => {
                  const file = e.target.files[0];
                  setSelectedFile(file);
                  setImageName(file?.name || "");
                }}
              />
            <br/>
              {mode === "image" && (
                <button className={`sih-mode-btn scan-btn ${mode === "image" ? "active-mode" : ""}`} onClick={handleImageScan}>
                  Image Scan
                </button>
              )}
              {mode === "deep" && (
                <button className={`sih-mode-btn scan-btn ${mode === "image" ? "active-mode" : ""}`} onClick={handleFullImageScan}>
                  Stego Scan
                </button>
              )}
            </section>
          )}

          {/* TEXT SCAN */}
          {mode === "text" && (
            <section className="sih-section">
              <h2 className="sih-section-title">Scan <span>Text / Email</span></h2>
              <textarea className="sih-textarea" placeholder="Paste email body or message..." rows={4}
                value={textBody} onChange={(e) => setTextBody(e.target.value)} />
              <button className="sih-btn-green full" onClick={handleTextScan}>Analyze Text</button>
            </section>
          )}

          {/* RESULTS AREA */}
          <section className="sih-result-area">
            {error && <div className="sih-result-box" style={{ color: "red" }}>{error}</div>}

            {loading && (
              <div className="sih-result-box">
                <div className="loader-sih"></div>
                <p>Analyzing...</p>
              </div>
            )}

            {/* Normal phishing result */}
            {!loading && result && (
              <div className="sih-result-box">
                <h3 className="result-title">{result.source} </h3>
              <h2>{result.status === "safe" ? "Legitimate" : "Phishing Likely"}</h2>
                <p className="result-desc">
                  {result.status === "safe"
                    ? "Looks safe based on current checks."
                    : "Strong phishing signals detected. Do NOT continue."}
                </p>
              </div>
            )}

            {/* Deep Scan Result */}
            {!loading && fullImageResult && (
              <div className="sih-result-box deep-panel">

                {fullImageResult.stego && (
                  <div className="deep-block">
                    <h4>🕵️ Steganography Detection</h4>
                    <p><b>Entropy:</b> {fullImageResult.stego.entropy}</p>
                    <p><b>LSB Prop Diff:</b> {fullImageResult.stego.lsb_prop_diff}</p>
                    <p><b>Chi-Square:</b> {fullImageResult.stego.chi_square}</p>
                    <p><b>Hidden Data Found:</b> {fullImageResult.stego.stego_detected ? "YES" : "NO"}</p>
                  </div>
                )}

                {fullImageResult.ocr && (
                  <div className="deep-block">
                    <h4>📝 Extracted OCR Text</h4>
                    <p>{fullImageResult.ocr}</p>
                  </div>
                )}

                {fullImageResult.yolo && (
                  <div className="deep-block">
                    <h4>🎯 UI Component Detection</h4>
                    <pre>{JSON.stringify(fullImageResult.yolo, null, 2)}</pre>
                  </div>
                )}
              </div>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
