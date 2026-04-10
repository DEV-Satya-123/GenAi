import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from '../utils/axios'

interface GitignoreStatus {
  has_gitignore: boolean
  missing_patterns: string[]
  recommendations: string[]
  auto_fix_available: boolean
}

export default function GitignoreManager() {
  const [status, setStatus] = useState<GitignoreStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [fixing, setFixing] = useState(false)
  const [projectType, setProjectType] = useState('python')
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  useEffect(() => {
    checkGitignore()
  }, [])

  const checkGitignore = async () => {
    setLoading(true)
    try {
      const response = await axios.get('/api/gitignore-check')
      setStatus(response.data)
      setLastChecked(new Date())
    } catch (error) {
      console.error('Failed to check .gitignore:', error)
    } finally {
      setLoading(false)
    }
  }

  const fixGitignore = async () => {
    setFixing(true)
    try {
      const response = await axios.post(`/api/gitignore-fix?project_type=${projectType}`)
      
      if (response.data.success) {
        // Show success message
        alert(response.data.message)
        // Refresh status
        await checkGitignore()
      } else {
        alert('Failed to fix .gitignore: ' + response.data.message)
      }
    } catch (error) {
      console.error('Failed to fix .gitignore:', error)
      alert('Failed to fix .gitignore')
    } finally {
      setFixing(false)
    }
  }

  const getStatusColor = () => {
    if (!status) return 'gray'
    if (!status.has_gitignore) return 'red'
    if (status.missing_patterns.length > 0) return 'yellow'
    return 'green'
  }

  const getStatusIcon = () => {
    const color = getStatusColor()
    
    if (color === 'green') {
      return (
        <svg className="w-6 h-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      )
    }
    
    if (color === 'yellow') {
      return (
        <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      )
    }
    
    return (
      <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700"
    >
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <svg className="w-6 h-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <h2 className="text-2xl font-bold text-white">.gitignore Manager</h2>
        </div>
        
        <button
          onClick={checkGitignore}
          disabled={loading}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors text-sm"
        >
          {loading ? 'Checking...' : 'Refresh'}
        </button>
      </div>

      {loading && !status ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <p className="text-gray-400 mt-2">Checking .gitignore status...</p>
        </div>
      ) : status ? (
        <div className="space-y-4">
          {/* Status Badge */}
          <div className="flex items-center gap-3 p-4 bg-gray-700 rounded-lg">
            {getStatusIcon()}
            <div className="flex-1">
              <p className="text-white font-semibold">
                {status.has_gitignore ? '.gitignore exists' : 'No .gitignore found'}
              </p>
              <p className="text-sm text-gray-400">
                {status.recommendations[0]}
              </p>
            </div>
          </div>

          {/* Missing Patterns */}
          {status.missing_patterns.length > 0 && (
            <div className="bg-yellow-900/20 border border-yellow-700/50 rounded-lg p-4">
              <h3 className="text-yellow-400 font-semibold mb-2 flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                Sensitive files not ignored ({status.missing_patterns.length})
              </h3>
              <div className="flex flex-wrap gap-2 mt-3">
                {status.missing_patterns.map((pattern, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-yellow-800/30 text-yellow-300 rounded-full text-sm font-mono"
                  >
                    {pattern}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Auto-fix Section */}
          {status.auto_fix_available && (
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-white font-semibold mb-3">Auto-fix Available</h3>
              
              <div className="flex items-center gap-3 mb-4">
                <label className="text-sm text-gray-400">Project Type:</label>
                <select
                  value={projectType}
                  onChange={(e) => setProjectType(e.target.value)}
                  className="px-3 py-2 bg-gray-600 border border-gray-500 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="python">Python</option>
                  <option value="node">Node.js</option>
                  <option value="java">Java</option>
                  <option value="general">General</option>
                </select>
              </div>

              <button
                onClick={fixGitignore}
                disabled={fixing}
                className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {fixing ? (
                  <>
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Fixing...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Fix .gitignore Automatically
                  </>
                )}
              </button>
            </div>
          )}

          {/* Success State */}
          {!status.auto_fix_available && status.has_gitignore && (
            <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4">
              <div className="flex items-center gap-2 text-green-400">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="font-semibold">All good! Your .gitignore is properly configured.</span>
              </div>
            </div>
          )}

          {/* Last Checked */}
          {lastChecked && (
            <p className="text-xs text-gray-500 text-center">
              Last checked: {lastChecked.toLocaleTimeString()}
            </p>
          )}
        </div>
      ) : null}
    </motion.div>
  )
}
