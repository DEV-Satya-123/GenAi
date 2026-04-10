import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import axios from '../utils/axios'

interface Commit {
  hash: string
  full_hash: string
  message: string
  author: string
  date: string
  files_changed: number
}

export default function CommitHistory() {
  const [commits, setCommits] = useState<Commit[]>([])
  const [loading, setLoading] = useState(true)
  const [maxCount, setMaxCount] = useState(10)

  useEffect(() => {
    fetchCommits()
  }, [maxCount])

  const fetchCommits = async () => {
    setLoading(true)
    try {
      const response = await axios.get(`/api/commit-history?max_count=${maxCount}`)
      setCommits(response.data.commits || [])
    } catch (error) {
      console.error('Failed to fetch commits:', error)
      setCommits([])
    } finally {
      setLoading(false)
    }
  }

  const copyHash = (hash: string) => {
    navigator.clipboard.writeText(hash)
  }

  const getCommitTypeColor = (message: string) => {
    const lowerMessage = message.toLowerCase()
    if (lowerMessage.startsWith('feat')) return 'text-green-400'
    if (lowerMessage.startsWith('fix')) return 'text-red-400'
    if (lowerMessage.startsWith('docs')) return 'text-blue-400'
    if (lowerMessage.startsWith('style')) return 'text-purple-400'
    if (lowerMessage.startsWith('refactor')) return 'text-yellow-400'
    if (lowerMessage.startsWith('test')) return 'text-pink-400'
    if (lowerMessage.startsWith('chore')) return 'text-gray-400'
    return 'text-white'
  }

  const getCommitTypeIcon = (message: string) => {
    const lowerMessage = message.toLowerCase()
    
    if (lowerMessage.startsWith('feat')) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
        </svg>
      )
    }
    
    if (lowerMessage.startsWith('fix')) {
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      )
    }
    
    return (
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
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
          <svg className="w-6 h-6 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-2xl font-bold text-white">Commit History</h2>
        </div>
        
        <div className="flex items-center gap-2">
          <select
            value={maxCount}
            onChange={(e) => setMaxCount(Number(e.target.value))}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value={5}>Last 5</option>
            <option value={10}>Last 10</option>
            <option value={20}>Last 20</option>
            <option value={50}>Last 50</option>
          </select>
          
          <button
            onClick={fetchCommits}
            disabled={loading}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors text-sm"
          >
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
          <p className="text-gray-400 mt-2">Loading commits...</p>
        </div>
      ) : commits.length === 0 ? (
        <div className="text-center py-8">
          <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p className="text-gray-400">No commits found</p>
        </div>
      ) : (
        <div className="space-y-2">
          {/* Timeline */}
          <div className="relative">
            {commits.map((commit, index) => (
              <motion.div
                key={commit.full_hash}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.05 }}
                className="relative pl-8 pb-6 last:pb-0"
              >
                {/* Timeline line */}
                {index < commits.length - 1 && (
                  <div className="absolute left-2 top-6 bottom-0 w-0.5 bg-gray-700"></div>
                )}
                
                {/* Timeline dot */}
                <div className={`absolute left-0 top-1 w-4 h-4 rounded-full border-2 border-gray-800 ${getCommitTypeColor(commit.message).replace('text-', 'bg-')}`}></div>
                
                {/* Commit card */}
                <div className="bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-colors border border-gray-600">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <button
                          onClick={() => copyHash(commit.hash)}
                          className="font-mono text-xs text-indigo-400 hover:text-indigo-300 transition-colors px-2 py-1 bg-gray-800 rounded"
                          title="Click to copy"
                        >
                          {commit.hash}
                        </button>
                        <span className="text-xs text-gray-500">•</span>
                        <span className="text-xs text-gray-400">{commit.date}</span>
                      </div>
                      
                      <div className="flex items-start gap-2 mb-2">
                        <span className={getCommitTypeColor(commit.message)}>
                          {getCommitTypeIcon(commit.message)}
                        </span>
                        <p className={`font-medium break-words ${getCommitTypeColor(commit.message)}`}>
                          {commit.message}
                        </p>
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-gray-400">
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                          {commit.author}
                        </span>
                        <span className="flex items-center gap-1">
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          {commit.files_changed} file{commit.files_changed !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </motion.div>
  )
}
