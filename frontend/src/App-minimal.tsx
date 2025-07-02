import { useState, useEffect } from 'react'

function App() {
const handleClick = () => {
alert('Button clicked! React is working!')
}

return (
<div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
<h1 style={{ color: 'green' }}> React is Working!</h1>
<p>This is a minimal React application to test functionality.</p>
<button
onClick={handleClick}
style={{
padding: '10px 20px',
fontSize: '16px',
backgroundColor: '#007bff',
color: 'white',
border: 'none',
borderRadius: '5px',
cursor: 'pointer'
}}
>
Click Me to Test Interactivity
</button>
<div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
<h3>System Status:</h3>
<ul>
<li>React: Mounted</li>
<li>TypeScript: Compiled</li>
<li>Vite: Serving</li>
<li>Interactive: Button clicks work</li>
</ul>
</div>
</div>
)
}

export default App