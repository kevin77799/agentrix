// In frontend/src/App.js

import React, { useState } from 'react';
import './App.css';

function App() {
  const [gps, setGps] = useState('17.3850, 78.4867');
  const [soilType, setSoilType] = useState('alluvial soil');
  const [advice, setAdvice] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    setAdvice(null);

    try {
      const response = await fetch('https://agentrix-silk.vercel.app/api/get-advice', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          gps: gps,
          soil_type: soilType,
          lang: 'en'
        })
      });

      const data = await response.json();

      if (response.ok) {
        setAdvice(data.advice);
      } else {
        setAdvice({ en: `Error: ${data.detail || 'Something went wrong'}` });
      }
    } catch (error) {
      setAdvice({ en: `Error: Could not connect to the backend. Is it running?` });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🌾 AgentriX Farming Assistant</h1>
        <p>Your AI-powered guide for smarter farming in Kerala.</p>
        <form onSubmit={handleSubmit} className="farm-form">
          <div className="form-group">
            <label htmlFor="gps">GPS Location</label>
            <input type="text" id="gps" value={gps} onChange={(e) => setGps(e.target.value)} />
          </div>
          <div className="form-group">
            <label htmlFor="soilType">Soil Type</label>
            <input type="text" id="soilType" value={soilType} onChange={(e) => setSoilType(e.target.value)} />
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Getting Advice...' : 'Get Farming Advice'}
          </button>
        </form>

        {advice && (
          <div className="advice-container">
            <div className="advice-card">
              <h2>Personalized Advice (English)</h2>
              <p>{advice.en}</p>
            </div>
            {advice.ml && (
              <div className="advice-card">
                <h2>വ്യക്തിഗത ഉപദേശം (മലയാളം)</h2>
                <p>{advice.ml}</p>
              </div>
            )}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;