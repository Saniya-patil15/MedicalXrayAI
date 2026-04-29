import React, { useState, useRef } from "react";
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
  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  React.useEffect(() => {
    if (chatOpen) {
      scrollToBottom();
    }
  }, [chatHistory, chatOpen]);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);

    if (selected) {
      setPreview(URL.createObjectURL(selected));
    } else {
      setPreview(null);
    }

    setResult(null);
    setSummary("");
    setChatHistory([]);
  };

  const handleAnalyze = async () => {
    if (!file) {
      alert("Please select an image first.");
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
      alert("Backend error or server is down.");
    }

    setLoading(false);
  };

  const handleChat = async () => {
    if (!question.trim()) return;
    if (!result || !summary) {
       alert("Please analyze an image first.");
       return;
    }

    const userQuestion = question;
    setQuestion("");

    const newHistory = [
      ...chatHistory,
      { role: "user", text: userQuestion },
    ];
    setChatHistory(newHistory);

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
        { role: "ai", text: data.answer },
      ]);
    } catch (error) {
      alert("Chat error or server is down.");
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1><span className="gradient-text">Medical AI</span> X-Ray Analysis</h1>
        <p className="subtitle"> Medical image analysis</p>
      </header>

      <main className="main-content">
        <div className="glass-card upload-section">
          <div className="controls-row">
            <div className="control-group">
              <label>Scan Type</label>
              <div className="radio-group">
                <label className={`radio-btn ${mode === "Chest" ? "active" : ""}`}>
                  <input
                    type="radio"
                    value="Chest"
                    checked={mode === "Chest"}
                    onChange={(e) => setMode(e.target.value)}
                  />
                  🫁 Chest
                </label>
                <label className={`radio-btn ${mode === "Bone" ? "active" : ""}`}>
                  <input
                    type="radio"
                    value="Bone"
                    checked={mode === "Bone"}
                    onChange={(e) => setMode(e.target.value)}
                  />
                  🦴 Bone
                </label>
              </div>
            </div>

            <div className="control-group">
              <label>Language</label>
              <select
                className="styled-select"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="English">English</option>
                <option value="Marathi">मराठी (Marathi)</option>
                <option value="Hindi">हिंदी (Hindi)</option>
              </select>
            </div>
          </div>

          <div className="file-upload-wrapper">
            <input type="file" id="file-upload" onChange={handleFileChange} accept="image/*" />
            <label htmlFor="file-upload" className="file-upload-label">
              <div className="upload-icon">📁</div>
              <span>{file ? file.name : "Click to select an X-Ray Image"}</span>
            </label>
          </div>

          {preview && (
            <div className="preview-container">
              <img src={preview} alt="X-ray preview" className="preview-img" />
            </div>
          )}

          <button 
            className={`analyze-btn ${loading ? "loading" : ""}`} 
            onClick={handleAnalyze}
            disabled={loading || !file}
          >
            {loading ? <span className="spinner">🔄</span> : "✨"} 
            {loading ? "Analyzing Image..." : "Analyze Image"}
          </button>
        </div>

        {(result || summary) && (
          <div className="results-container">
            {result && (
              <div className="glass-card result-card bounce-in">
                <h3>📊 Analysis Result</h3>
                <div className="result-data">
                  <div className="data-box">
                    <span className="data-label">Prediction</span>
                    <span className="data-value highlight">{result.prediction}</span>
                  </div>
                  <div className="data-box">
                    <span className="data-label">Confidence</span>
                    <span className="data-value">{(result.confidence * 100).toFixed(2)}%</span>
                  </div>
                </div>
              </div>
            )}

            {summary && (
              <div className="glass-card summary-card fade-in">
                <h3>📝 Medical Summary</h3>
                <p className="summary-text">{summary}</p>
              </div>
            )}
          </div>
        )}
      </main>

      {/* Floating Chat Button */}
      {(result && summary) && (
        <button
          className={`chat-fab ${chatOpen ? "active" : "pulse"}`}
          onClick={() => setChatOpen(!chatOpen)}
          aria-label="Toggle Chat"
        >
          {chatOpen ? "✕" : "💬"}
        </button>
      )}

      {/* Chat Popup */}
      <div className={`chat-window ${chatOpen ? "open" : ""}`}>
        <div className="chat-header">
          <div className="chat-title">
            <span className="bot-icon">🤖</span> AI Assistant
          </div>
          <button className="close-btn" onClick={() => setChatOpen(false)}>✕</button>
        </div>

        <div className="chat-body">
          {chatHistory.length === 0 ? (
            <div className="chat-empty">
              <p>Hello! I have analyzed your report. Ask me any questions you have.</p>
            </div>
          ) : (
            chatHistory.map((msg, index) => (
              <div
                key={index}
                className={`chat-message-wrapper ${msg.role === "user" ? "user-wrapper" : "ai-wrapper"}`}
              >
                <div className={`chat-bubble ${msg.role}`}>
                  {msg.text}
                </div>
              </div>
            ))
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="chat-footer">
          <input
            type="text"
            placeholder="Type your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleChat()}
            className="chat-input"
          />
          <button className="chat-send-btn" onClick={handleChat}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;