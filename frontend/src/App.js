import React, { useState } from "react";
import "./App.css";

function App() {
  const [mode, setMode] = useState("Chest");
  const [language, setLanguage] = useState("English");

  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const [result, setResult] = useState(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const [question, setQuestion] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatOpen, setChatOpen] = useState(false);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);

    if (selected) {
      setPreview(URL.createObjectURL(selected));
    }

    setResult(null);
    setSummary("");
    setChatHistory([]);
  };

  const handleAnalyze = async () => {
    if (!file) {
      alert("Please select image");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const analyzeUrl =
      mode === "Chest"
        ? "http://127.0.0.1:8000/analyze-chest"
        : "http://127.0.0.1:8000/analyze-bone";

    setLoading(true);
    setResult(null);
    setSummary("");
    setChatHistory([]);

    try {
      // Analyze
      const response = await fetch(analyzeUrl, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResult(data);

      // Summary
      const summaryRes = await fetch(
        "http://127.0.0.1:8000/generate-summary",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            finding: data.prediction,
            confidence: data.confidence,
            language: language,
            analysis_mode: mode,
          }),
        }
      );

      const summaryData = await summaryRes.json();
      setSummary(summaryData.summary);

    } catch (error) {
      alert("Backend error");
    }

    setLoading(false);
  };

  const handleChat = async () => {
    if (!question.trim()) return;
    if (!result || !summary) return;

    const userQuestion = question;
    setQuestion("");

    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          finding: result.prediction,
          confidence: result.confidence,
          summary: summary,
          question: userQuestion,
          language: language,
        }),
      });

      const data = await res.json();

      setChatHistory((prev) => [
        ...prev,
        { role: "user", text: userQuestion },
        { role: "ai", text: data.answer },
      ]);

      setChatOpen(true);

    } catch (error) {
      alert("Chat error");
    }
  };

  return (
    <div className="app">
      <h1>🩺 AI Medical X-Ray Analysis System</h1>

      <div className="card">
        <h2>Upload {mode} X-ray</h2>

        {/* X-ray Type */}
        <div style={{ marginBottom: "20px" }}>
          <label>
            <input
              type="radio"
              value="Chest"
              checked={mode === "Chest"}
              onChange={(e) => setMode(e.target.value)}
            />
            Chest
          </label>

          <label style={{ marginLeft: "20px" }}>
            <input
              type="radio"
              value="Bone"
              checked={mode === "Bone"}
              onChange={(e) => setMode(e.target.value)}
            />
            Bone
          </label>
        </div>

        {/* Language */}
        <div style={{ marginBottom: "20px" }}>
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            style={{
              padding: "10px",
              borderRadius: "10px",
              border: "1px solid #ccc",
              width: "220px",
            }}
          >
            <option value="English">English</option>
            <option value="Marathi">Marathi</option>
            <option value="Hindi">Hindi</option>
          </select>
        </div>

        {/* Upload */}
        <input type="file" onChange={handleFileChange} />

        {/* Preview */}
        {preview && (
          <div style={{ marginTop: "20px" }}>
            <img
              src={preview}
              alt="preview"
              style={{
                width: "260px",
                borderRadius: "12px",
                boxShadow: "0 8px 18px rgba(0,0,0,0.08)",
              }}
            />
          </div>
        )}

        <br />
        <br />

        {/* Analyze */}
        <button onClick={handleAnalyze}>
          {loading ? "Analyzing..." : "Analyze"}
        </button>

        {/* Result */}
        {result && (
          <div className="result">
            <h3>Analysis Result</h3>

            <p>
              <strong>Prediction:</strong> {result.prediction}
            </p>

            <p>
              <strong>Confidence:</strong>{" "}
              {(result.confidence * 100).toFixed(2)}%
            </p>
          </div>
        )}

        {/* Summary */}
        {summary && (
          <div className="result">
            <h3>Medical Summary</h3>

            <p style={{ whiteSpace: "pre-line" }}>{summary}</p>
          </div>
        )}
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setChatOpen(!chatOpen)}
        style={{
          position: "fixed",
          bottom: "25px",
          right: "25px",
          width: "65px",
          height: "65px",
          borderRadius: "50%",
          fontSize: "26px",
          zIndex: 999,
        }}
      >
        💬
      </button>

      {/* Chat Popup */}
      {chatOpen && (
        <div
          style={{
            position: "fixed",
            bottom: "100px",
            right: "25px",
            width: "340px",
            height: "500px",
            background: "white",
            borderRadius: "18px",
            boxShadow: "0 10px 35px rgba(0,0,0,0.18)",
            display: "flex",
            flexDirection: "column",
            zIndex: 999,
            overflow: "hidden",
          }}
        >
          {/* Header */}
          <div
            style={{
              background: "#2563eb",
              color: "white",
              padding: "15px",
              fontWeight: "bold",
              display: "flex",
              justifyContent: "space-between",
            }}
          >
            <span>🤖 Medical AI Chat</span>

            <span
              style={{ cursor: "pointer" }}
              onClick={() => setChatOpen(false)}
            >
              ✖
            </span>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: "12px",
              overflowY: "auto",
              background: "#f9fafb",
            }}
          >
            {chatHistory.length === 0 ? (
              <p style={{ color: "#666" }}>
                Ask any question about your report.
              </p>
            ) : (
              chatHistory.map((msg, index) => (
                <div
                  key={index}
                  style={{
                    marginBottom: "10px",
                    textAlign:
                      msg.role === "user" ? "right" : "left",
                  }}
                >
                  <div
                    style={{
                      display: "inline-block",
                      padding: "10px 12px",
                      borderRadius: "12px",
                      maxWidth: "80%",
                      background:
                        msg.role === "user"
                          ? "#2563eb"
                          : "#e5e7eb",
                      color:
                        msg.role === "user"
                          ? "white"
                          : "black",
                    }}
                  >
                    {msg.text}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Input */}
          <div
            style={{
              padding: "10px",
              display: "flex",
              gap: "8px",
              borderTop: "1px solid #eee",
            }}
          >
            <input
              type="text"
              placeholder="Type message..."
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              style={{
                flex: 1,
                padding: "10px",
                borderRadius: "10px",
                border: "1px solid #ccc",
              }}
            />

            <button onClick={handleChat}>Send</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;