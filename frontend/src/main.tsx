import React from "react"
import ReactDOM from "react-dom/client"
import App from "./App.tsx"
import "./index.css"

console.log("🚀 Main.tsx loaded - Starting React initialization...")

const rootElement = document.getElementById("root")
console.log("Root element found:", rootElement)

if (!rootElement) {
  console.error("❌ Root element not found! Cannot mount React app.")
  document.body.innerHTML = "<div style=\"padding: 20px; background: red; color: white; font-size: 24px;\">❌ CRITICAL ERROR: Root element not found</div>"
} else {
  try {
    console.log("✅ Creating React root...")
    const root = ReactDOM.createRoot(rootElement)
    console.log("✅ React root created, rendering App...")
    
    root.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>
    )
    
    console.log("✅ React app render initiated")
  } catch (error) {
    console.error("❌ Error during React initialization:", error)
    document.body.innerHTML = `<div style="padding: 20px; background: red; color: white; font-size: 18px;">❌ REACT ERROR: ${error}</div>`
  }
}
