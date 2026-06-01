import React, { useState } from "react";
import "../popup/popup.css";
import { checkURL } from "../utils/urlCheck";
import { checkImage } from "../utils/imageCheck";

export default function Popup() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);

  const handleCheck = async () => {
    const data = await checkURL(url);
    setResult(data);
  };

  return (
    <div className="popup-root">
      <h2>Phish Busterz</h2>

      <input
        type="text"
        placeholder="Enter URL..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />

      <button onClick={handleCheck}>Analyze URL</button>

      {result && (
        <div className="result-box">
          <p>Status: {result.verdict}</p>
          <p>Probability: {result.phishing_probability}</p>
        </div>
      )}
    </div>
  );
}
