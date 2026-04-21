import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'
import Header from './components/Header'
import StatusCard from './components/StatusCard'
import RepositoryManager from './components/RepositoryManager'
import RepositoryOverview from './components/RepositoryOverview'
import Login from './components/Login'
import Register from './components/Register'
import SearchCommits from './components/SearchCommits'
import GitignoreManager from './components/GitignoreManager'
import CommitHistory from './components/CommitHistory'
import RemoteStatusBanner from './components/RemoteStatusBanner'

type Page = 'dashboard' | 'overview'

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [currentRepoPath, setCurrentRepoPath] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [showRegister, setShowRegister] = useState(false)
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [currentPage, setCurrentPage] = useState<Page>('dashboard')

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('auth_token')
    if (token) {
      setAuthToken(token)
      setIsAuthenticated(true)
    }
  }, [])

  const handleLoginSuccess = (token: string) => {
    setAuthToken(token)
    setIsAuthenticated(true)
  }

  const handleRegisterSuccess = () => {
    setShowRegister(false)
    // Show success message or auto-login
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    setAuthToken(null)
    setIsAuthenticated(false)
    setCurrentPage('dashboard')
  }

  const handleRepositoryChange = (repoPath: string) => {
    setCurrentRepoPath(repoPath)
  }

  const handleShowOverview = () => {
    setCurrentPage('overview')
  }

  const handleBackToDashboard = () => {
    setCurrentPage('dashboard')
  }

  // Show login/register if not authenticated
  if (!isAuthenticated) {
    if (showRegister) {
      return (
        <Register
          onRegisterSuccess={handleRegisterSuccess}
          onSwitchToLogin={() => setShowRegister(false)}
        />
      )
    }
    return (
      <Login
        onLoginSuccess={handleLoginSuccess}
        onSwitchToRegister={() => setShowRegister(true)}
      />
    )
  }

  // Show Overview Page
  if (currentPage === 'overview') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <Header onLogout={handleLogout} />
        <RepositoryOverview onClose={handleBackToDashboard} />
      </div>
    )
  }

  // Show main dashboard
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header onLogout={handleLogout} />

      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl font-bold text-center mb-4 gradient-text">
            AI Git Automation
          </h1>
          <p className="text-center text-blue-800 mb-12 text-2xl">
            Intelligent commit message generation powered by Agent
          </p>
        </motion.div>

        <RepositoryManager 
          onRepositoryChange={handleRepositoryChange}
          onShowOverview={handleShowOverview}
        />

        {/* Remote Status Banner - Shows GitHub changes */}
        <RemoteStatusBanner />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <StatusCard />
        </div>

        <Dashboard
          onRunStart={() => setIsRunning(true)}
          onRunEnd={() => setIsRunning(false)}
        />

        {/* New Features Section */}
        <div className="mt-8 space-y-6">
          {/* .gitignore Manager */}
          <GitignoreManager />

          {/* Search and History in Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SearchCommits />
            <CommitHistory />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
