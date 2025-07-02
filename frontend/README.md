# Multi-Market Correlation Engine - TypeScript Frontend

An impressive and functional TypeScript React frontend for the Multi-Market Correlation Engine with FAISS Vector Database and Llama LLM integration.

## Features

### ✨ Beautiful & Modern UI
- **Material Design Inspired**: Clean, modern interface with Tailwind CSS
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark/Light Theme**: Elegant design with smooth animations
- **Component Library**: Reusable, type-safe React components

### 🧠 AI-Powered Interface
- **LLM Assistant**: Real-time chat with Llama-powered financial AI
- **Vector Search**: FAISS semantic pattern search with beautiful results
- **Market Analysis**: Advanced correlation visualization and insights
- **Smart Recommendations**: AI-generated portfolio optimization

### Advanced Analytics
- **Real-time Charts**: Interactive charts with Recharts
- **Correlation Matrices**: Beautiful heatmaps and analysis
- **Performance Tracking**: Portfolio and market performance
- **Custom Dashboards**: Configurable analytics panels

### Technical Excellence
- **TypeScript**: Fully typed codebase for reliability
- **React 19**: Latest React with modern hooks and patterns
- **Vite**: Lightning-fast development and build
- **React Query**: Smart data fetching and caching
- **Framer Motion**: Smooth animations and transitions

## 🏗 Architecture

```
frontend/
├── src/
│ ├── components/ # Reusable UI components
│ │ ├── ui/ # Basic UI components (Card, Button, etc.)
│ │ └── layout/ # Layout components (Sidebar, Header)
│ ├── pages/ # Main application pages
│ │ ├── Dashboard.tsx # Overview dashboard
│ │ ├── LLMAssistant.tsx# AI chat interface
│ │ ├── VectorSearch.tsx# FAISS pattern search
│ │ ├── MarketAnalysis.tsx # Charts and correlations
│ │ └── Portfolio.tsx # Portfolio management
│ ├── api/ # API client and services
│ │ └── client.ts # Axios-based API client
│ ├── types/ # TypeScript type definitions
│ │ └── index.ts # All application types
│ ├── hooks/ # Custom React hooks
│ ├── utils/ # Utility functions
│ └── assets/ # Static assets
├── public/ # Public assets
├── index.html # HTML entry point
├── vite.config.ts # Vite configuration
├── tailwind.config.js # Tailwind CSS configuration
├── tsconfig.json # TypeScript configuration
└── package.json # Dependencies and scripts
```

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn
- Multi-Market Correlation Engine API running on port 8000

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Development Commands

```bash
# Development
npm run dev # Start dev server (http://localhost:3000)
npm run build # Build for production
npm run preview # Preview production build
npm run lint # Run ESLint
npm run type-check # TypeScript type checking
```

## Pages & Features

### Dashboard
- **Real-time Metrics**: Portfolio value, correlations, vector patterns
- **Interactive Charts**: Market performance and trend analysis
- **Activity Feed**: Latest system events and updates
- **Quick Actions**: Direct access to key features

### LLM Assistant
- **Chat Interface**: Natural language queries with AI responses
- **Suggested Questions**: Pre-built financial analysis prompts
- **Markdown Support**: Rich text formatting in responses
- **Conversation History**: Persistent chat sessions
- **Real-time Status**: LLM model availability indicators

### Vector Search
- **Semantic Search**: FAISS-powered pattern matching
- **Pattern Filters**: Filter by type, symbol, or metadata
- **Similarity Scoring**: Visual similarity indicators
- **Pattern Analytics**: Database statistics and distribution
- **Advanced Results**: Rich metadata and visualization

### Market Analysis
- **Symbol Selection**: Multi-asset analysis interface
- **Time Range Controls**: Flexible time period selection
- **Interactive Charts**: Zoomable, responsive price charts
- **Correlation Matrix**: Beautiful heatmap visualization
- **AI Insights**: Automated pattern recognition

### 💼 Portfolio (Coming Soon)
- Portfolio optimization
- Risk analysis
- Rebalancing recommendations
- Performance tracking

### Reports (Coming Soon)
- Custom report generation
- Export capabilities
- Scheduled reports
- Analytics dashboards

## UI Components

### Layout Components
- **Sidebar**: Responsive navigation with icons and descriptions
- **Header**: Status indicators, search, notifications
- **Layout**: Main application shell with mobile support

### UI Components
- **Card**: Flexible content containers with loading states
- **LoadingSpinner**: Animated loading indicators
- **Charts**: Recharts-based financial visualizations
- **Forms**: Type-safe form components with validation

## 🔌 API Integration

The frontend communicates with the backend through a comprehensive API client:

```typescript
// Example API usage
import apiClient from '@/api/client'

// Health check
const health = await apiClient.healthCheck()

// LLM chat
const response = await apiClient.sendChatMessage({
message: "What are the current market correlations?"
})

// Vector search
const patterns = await apiClient.searchVectorPatterns({
query: "high volatility tech stocks",
k: 10
})

// Market data
const data = await apiClient.getMarketData(
['AAPL', 'MSFT'],
'1Y'
)
```

## State Management

- **React Query**: Server state management and caching
- **React Hooks**: Local state management
- **Context API**: Global application state
- **TypeScript**: Type-safe state operations

## Styling & Design

### Tailwind CSS
- **Custom Theme**: Financial application color palette
- **Responsive Design**: Mobile-first approach
- **Component Classes**: Reusable utility classes
- **Dark Mode Ready**: Prepared for theme switching

### Design System
- **Colors**: Primary, secondary, success, warning, error
- **Typography**: Inter font family with size scale
- **Spacing**: Consistent margin and padding scale
- **Shadows**: Layered elevation system

## Configuration

### Environment Variables
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_WS_URL=ws://127.0.0.1:8000/ws
```

### API Proxy
The development server proxies API requests to the backend:
```typescript
// vite.config.ts
export default defineConfig({
server: {
proxy: {
'/api': {
target: 'http://127.0.0.1:8000',
changeOrigin: true,
rewrite: (path) => path.replace(/^\/api/, ''),
},
},
},
})
```

## Mobile Support

- **Responsive Sidebar**: Collapsible mobile navigation
- **Touch-Friendly**: Optimized for mobile interactions
- **Performance**: Optimized for mobile performance
- **PWA Ready**: Progressive Web App capabilities

## Performance

- **Code Splitting**: Route-based code splitting
- **Lazy Loading**: Component-level lazy loading
- **Caching**: Smart API response caching
- **Optimizations**: Production build optimizations

## 🧪 Development

### File Structure
```
src/
├── components/ui/ # Basic UI components
├── components/layout/ # Layout components
├── pages/ # Route components
├── api/ # API client
├── types/ # TypeScript types
├── hooks/ # Custom hooks
└── utils/ # Utilities
```

### Code Style
- **TypeScript**: Strict mode with full type coverage
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **Imports**: Absolute imports with `@/` prefix

## Features in Detail

### Real-time Updates
- WebSocket integration for live data
- Automatic reconnection handling
- Optimistic updates

### Error Handling
- Global error boundaries
- API error handling
- User-friendly error messages
- Retry mechanisms

### Accessibility
- WCAG 2.1 compliant
- Keyboard navigation
- Screen reader support
- Focus management

## Deployment

### Production Build
```bash
npm run build
```

### Deployment Options
- **Vercel**: Zero-config deployment
- **Netlify**: Static site hosting
- **Docker**: Containerized deployment
- **AWS S3**: Static hosting with CloudFront

## 🔗 Integration

### Backend API
- RESTful API integration
- Real-time WebSocket connections
- File upload/download support
- Authentication ready

### External Services
- Market data APIs
- AI/ML model endpoints
- Vector database connections
- Notification services

## Documentation

- **Component Docs**: Storybook integration ready
- **API Docs**: OpenAPI/Swagger integration
- **Type Docs**: Generated TypeScript documentation
- **User Guide**: In-app help and tutorials

## Getting Started

1. **Start the Backend**: Ensure the API server is running on port 8000
2. **Install Dependencies**: `npm install`
3. **Start Development**: `npm run dev`
4. **Open Browser**: Visit http://localhost:3000
5. **Explore Features**: Navigate through the different pages

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

---

**Built with for the Multi-Market Correlation Engine**

*A beautiful, functional TypeScript frontend that brings advanced financial analysis to life.*