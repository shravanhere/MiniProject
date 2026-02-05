# Encroachment Detection System - Frontend

A professional, production-ready React application for automated detection of encroachments on public land.

## 🚀 Features

- **Modern UI/UX**: Clean, professional interface with smooth animations
- **Authentication**: Secure login/logout system
- **Dashboard**: Real-time statistics and visualizations
- **Charts & Analytics**: Interactive data visualization with Recharts
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Error Handling**: Comprehensive error handling and user feedback
- **Type Safety**: Structured API communication

## 📋 Prerequisites

- Node.js 16+ and npm
- Backend API running on port 5000

## 🛠️ Installation

1. **Install dependencies:**
```bash
npm install
```

2. **Configure environment:**
```bash
cp .env.example .env
```

Edit `.env` and set your backend API URL:
```
VITE_API_URL=http://localhost:5000/api
```

3. **Start development server:**
```bash
npm run dev
```

The application will run on `http://localhost:3000`

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── Header.jsx       # Top navigation bar
│   ├── Sidebar.jsx      # Side navigation
│   └── StatsCard.jsx    # Statistics card component
├── contexts/            # React Context providers
│   └── AuthContext.jsx  # Authentication state management
├── pages/               # Page components
│   ├── Login.jsx        # Login page
│   └── Dashboard.jsx    # Main dashboard
├── services/            # API communication
│   └── api.js          # Centralized API client
├── App.jsx             # Main app component with routing
├── main.jsx            # Application entry point
└── index.css           # Global styles
```

## 🎨 Design System

The application uses a professional civic tech design system:

- **Colors**: Blue primary palette with accent colors
- **Typography**: IBM Plex Sans for UI, JetBrains Mono for code
- **Components**: Consistent spacing, shadows, and border radius
- **Animations**: Smooth transitions and micro-interactions

## 🔐 Authentication

### Demo Credentials
```
Email: admin@example.com
Password: admin123
```

### How it works:
1. User logs in with email/password
2. Backend returns JWT token
3. Token stored in localStorage
4. Token sent with all API requests
5. Automatic redirect to login on 401 errors

## 📡 API Integration

All API calls are centralized in `src/services/api.js`:

```javascript
import { authAPI, imageAPI, detectionAPI, encroachmentAPI } from './services/api';

// Example usage
const result = await authAPI.login(email, password);
const images = await imageAPI.getAll();
const stats = await encroachmentAPI.getStatistics();
```

### Available API Methods:

**Authentication:**
- `authAPI.login(credentials)`
- `authAPI.register(userData)`
- `authAPI.logout()`
- `authAPI.getCurrentUser()`

**Images:**
- `imageAPI.upload(formData, onProgress)`
- `imageAPI.getAll()`
- `imageAPI.getById(id)`
- `imageAPI.delete(id)`

**Detection:**
- `detectionAPI.runDetection(imageId)`
- `detectionAPI.getResults(detectionId)`
- `detectionAPI.getAllDetections()`
- `detectionAPI.getStats()`

**Encroachments:**
- `encroachmentAPI.getAll(params)`
- `encroachmentAPI.getById(id)`
- `encroachmentAPI.verify(id, status, remarks)`
- `encroachmentAPI.getReport(id)`
- `encroachmentAPI.getStatistics()`

## 🔧 Configuration

### Proxy Setup
The Vite config includes a proxy to avoid CORS issues during development:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true,
    }
  }
}
```

This means requests to `/api/*` are automatically forwarded to `http://localhost:5000/api/*`

## 🚀 Building for Production

```bash
npm run build
```

This creates an optimized build in the `dist/` folder.

### Preview production build:
```bash
npm run preview
```

## 🐛 Troubleshooting

### Blank white screen after login
1. Check browser console (F12) for errors
2. Verify backend is running on the correct port
3. Check CORS configuration on backend
4. Ensure API endpoints match between frontend and backend

### API calls failing
1. Check network tab in browser dev tools
2. Verify backend URL in `.env` file
3. Check if backend is running: `curl http://localhost:5000/api/health`
4. Review CORS headers on backend

### Authentication issues
1. Clear localStorage: `localStorage.clear()`
2. Check token format from backend
3. Verify token is being sent in Authorization header
4. Check backend authentication middleware

## 📝 Development Notes

### Adding New Pages
1. Create page component in `src/pages/`
2. Create corresponding CSS file
3. Add route in `src/App.jsx`
4. Add navigation link in `src/components/Sidebar.jsx`

### API Error Handling
All API calls automatically:
- Add authentication tokens to requests
- Handle 401 errors (redirect to login)
- Return structured error messages

### State Management
- Authentication: React Context (`AuthContext`)
- Component state: React hooks (`useState`, `useEffect`)
- For complex state, consider adding Redux or Zustand

## 🎯 Next Steps

To extend this application:

1. **Add more pages:**
   - Upload page for image submission
   - Map view with Leaflet integration
   - Detections list with filters
   - Reports generation
   - Settings page

2. **Enhance features:**
   - Real-time notifications
   - Advanced filtering and search
   - Export functionality
   - User management
   - Role-based access control

3. **Improve UX:**
   - Loading skeletons
   - Optimistic updates
   - Better error messages
   - Toast notifications

## 📄 License

This project is for educational/demonstration purposes.

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review browser console for errors
3. Verify backend API is working correctly
4. Check network requests in dev tools

---

Built with React, Vite, and modern web technologies 🚀
