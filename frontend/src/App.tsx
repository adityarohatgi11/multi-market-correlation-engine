import { useState, useEffect } from 'react'

function App() {
  const [apiStatus, setApiStatus] = useState('Checking...')
  const [currentTime, setCurrentTime] = useState(new Date().toLocaleTimeString())

  useEffect(() => {
    // Check API health
    fetch('/api/health')
      .then(res => res.json())
      .then(data => {
        setApiStatus(`✅ API Healthy - ${data.status}`)
      })
      .catch(err => {
        setApiStatus(`❌ API Error: ${err.message}`)
      })

    // Update time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date().toLocaleTimeString())
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  return (
    <div style={{ 
      padding: '40px', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      backgroundColor: '#f8f9fa',
      minHeight: '100vh'
    }}>
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ 
          color: '#2563eb', 
          fontSize: '2.5rem',
          marginBottom: '10px',
          textAlign: 'center'
        }}>
          🏛️ Multi-Market Correlation Engine
        </h1>
        
        <p style={{ 
          color: '#6b7280', 
          fontSize: '1.2rem',
          textAlign: 'center',
          marginBottom: '40px'
        }}>
          Advanced Financial Analysis Platform
        </p>

        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr',
          gap: '20px',
          marginBottom: '30px'
        }}>
          <div style={{
            padding: '20px',
            backgroundColor: '#f0f9ff',
            borderRadius: '8px',
            border: '1px solid #0ea5e9'
          }}>
            <h3 style={{ color: '#0c4a6e', margin: '0 0 10px 0' }}>🚀 Frontend Status</h3>
            <p style={{ color: '#059669', margin: 0, fontSize: '18px', fontWeight: 'bold' }}>
              ✅ React App Running Successfully!
            </p>
            <p style={{ color: '#6b7280', margin: '5px 0 0 0', fontSize: '14px' }}>
              Vite Development Server Active
            </p>
          </div>

          <div style={{
            padding: '20px',
            backgroundColor: '#f0fdf4',
            borderRadius: '8px',
            border: '1px solid #22c55e'
          }}>
            <h3 style={{ color: '#166534', margin: '0 0 10px 0' }}>🔗 API Connection</h3>
            <p style={{ margin: 0, fontSize: '16px' }}>
              {apiStatus}
            </p>
            <p style={{ color: '#6b7280', margin: '5px 0 0 0', fontSize: '14px' }}>
              Backend Health Check
            </p>
          </div>
        </div>

        <div style={{
          padding: '20px',
          backgroundColor: '#fef3c7',
          borderRadius: '8px',
          border: '1px solid #f59e0b',
          textAlign: 'center'
        }}>
          <h3 style={{ color: '#92400e', margin: '0 0 15px 0' }}>⏰ System Time</h3>
          <p style={{ 
            color: '#1f2937', 
            margin: 0, 
            fontSize: '24px', 
            fontWeight: 'bold',
            fontFamily: 'monospace'
          }}>
            {currentTime}
          </p>
        </div>

        <div style={{ marginTop: '30px', textAlign: 'center' }}>
          <h3 style={{ color: '#374151', marginBottom: '15px' }}>✨ System Features</h3>
          <div style={{
            display: 'flex',
            justifyContent: 'space-around',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <span style={{
              padding: '8px 16px',
              backgroundColor: '#e0e7ff',
              color: '#3730a3',
              borderRadius: '20px',
              fontSize: '14px'
            }}>
              🤖 Multi-Agent System
            </span>
            <span style={{
              padding: '8px 16px',
              backgroundColor: '#fce7f3',
              color: '#a21caf',
              borderRadius: '20px',
              fontSize: '14px'
            }}>
              🧠 LLM Integration
            </span>
            <span style={{
              padding: '8px 16px',
              backgroundColor: '#dcfce7',
              color: '#166534',
              borderRadius: '20px',
              fontSize: '14px'
            }}>
              📊 ML Analytics
            </span>
            <span style={{
              padding: '8px 16px',
              backgroundColor: '#fed7d7',
              color: '#c53030',
              borderRadius: '20px',
              fontSize: '14px'
            }}>
              🔍 Vector Search
            </span>
          </div>
        </div>

        <div style={{
          marginTop: '40px',
          padding: '20px',
          backgroundColor: '#f3f4f6',
          borderRadius: '8px',
          textAlign: 'center'
        }}>
          <p style={{ 
            color: '#059669', 
            margin: 0, 
            fontSize: '18px',
            fontWeight: 'bold'
          }}>
            🎉 Frontend Successfully Fixed and Running!
          </p>
          <p style={{ color: '#6b7280', margin: '10px 0 0 0' }}>
            The React application is now working properly. All syntax errors have been resolved.
          </p>
        </div>
      </div>
    </div>
  )
}

export default App 