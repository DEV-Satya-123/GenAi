import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import axios from '../utils/axios'

interface RemoteStatus {
    is_behind: boolean
    commits_behind: number
    remote_commits: Array<{
        hash: string
        message: string
        author: string
        date: string
    }>
    potential_conflicts: string[]
    recommendation: string
    safe_to_commit: boolean
}

export default function RemoteStatusBanner() {
    const [status, setStatus] = useState<RemoteStatus | null>(null)
    const [loading, setLoading] = useState(false)
    const [dismissed, setDismissed] = useState(false)
    const [expanded, setExpanded] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [lastChecked, setLastChecked] = useState<Date | null>(null)

    useEffect(() => {
        checkRemoteStatus()

        // Auto-check every 5 minutes
        const interval = setInterval(checkRemoteStatus, 5 * 60 * 1000)

        return () => clearInterval(interval)
    }, [])

    const checkRemoteStatus = async () => {
        setLoading(true)
        setError(null)
        try {
            const response = await axios.get('/api/remote-status')
            if (response.data.success) {
                setStatus(response.data)
                setDismissed(false) // Show again if new changes
                setLastChecked(new Date())
            } else {
                setError(response.data.message || 'Failed to check remote')
            }
        } catch (error: any) {
            console.error('Failed to check remote status:', error)
            setError(error.response?.data?.detail || 'Failed to check remote status')
        } finally {
            setLoading(false)
        }
    }

    const copyPullCommand = () => {
        navigator.clipboard.writeText('git pull origin main')

        // Show toast
        const toast = document.createElement('div')
        toast.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-50'
        toast.textContent = 'Copied: git pull origin main'
        document.body.appendChild(toast)
        setTimeout(() => toast.remove(), 2000)
    }

    if (!status || !status.is_behind || dismissed) {
        // Show compact status indicator when up-to-date
        return (
            <div className="mb-6 rounded-lg border border-gray-700 bg-gray-800/50 p-3 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    {loading ? (
                        <>
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-400"></div>
                            <span className="text-gray-400 text-sm">Checking GitHub for changes...</span>
                        </>
                    ) : error ? (
                        <>
                            <svg className="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-red-400 text-sm">{error}</span>
                        </>
                    ) : (
                        <>
                            <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span className="text-green-400 text-sm font-medium">✅ Up to date with GitHub</span>
                            {lastChecked && (
                                <span className="text-gray-500 text-xs">
                                    • Last checked {lastChecked.toLocaleTimeString()}
                                </span>
                            )}
                        </>
                    )}
                </div>
                <button
                    onClick={checkRemoteStatus}
                    disabled={loading}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 text-white rounded text-xs transition-colors"
                >
                    {loading ? 'Checking...' : 'Check Now'}
                </button>
            </div>
        )
    }

    const hasConflicts = status.potential_conflicts && status.potential_conflicts.length > 0
    const bgColor = hasConflicts ? 'bg-red-900/20 border-red-500' : 'bg-yellow-900/20 border-yellow-500'
    const iconColor = hasConflicts ? 'text-red-400' : 'text-yellow-400'

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className={`mb-6 rounded-lg border-2 ${bgColor} p-4`}
            >
                {/* Header */}
                <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1">
                        <svg className={`w-6 h-6 ${iconColor} flex-shrink-0 mt-1`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>

                        <div className="flex-1">
                            <h3 className={`font-semibold ${iconColor} mb-1`}>
                                {hasConflicts ? '🚨 Conflict Warning' : '💡 Remote Changes Detected'}
                            </h3>

                            <p className="text-white mb-2">
                                GitHub has <span className="font-semibold">{status.commits_behind}</span> new commit{status.commits_behind !== 1 ? 's' : ''} since your last push
                            </p>

                            {hasConflicts && (
                                <div className="bg-red-900/30 border border-red-700 rounded p-3 mb-3">
                                    <p className="text-red-300 font-semibold mb-2">
                                        ⚠️ {status.potential_conflicts.length} file(s) you're editing were also changed on remote:
                                    </p>
                                    <ul className="text-red-200 text-sm space-y-1">
                                        {status.potential_conflicts.slice(0, 3).map((file, i) => (
                                            <li key={i} className="font-mono">• {file}</li>
                                        ))}
                                        {status.potential_conflicts.length > 3 && (
                                            <li className="text-red-400">... and {status.potential_conflicts.length - 3} more</li>
                                        )}
                                    </ul>
                                </div>
                            )}

                            <p className="text-gray-300 text-sm mb-3">
                                {status.recommendation}
                            </p>

                            {/* Action Buttons */}
                            <div className="flex flex-wrap gap-2">
                                <button
                                    onClick={copyPullCommand}
                                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors flex items-center gap-2 shadow-lg"
                                >
                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                                    </svg>
                                    📋 Copy Pull Command
                                </button>

                                <button
                                    onClick={() => setExpanded(!expanded)}
                                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm transition-colors"
                                >
                                    {expanded ? 'Hide Details' : 'View Details'}
                                </button>

                                <button
                                    onClick={checkRemoteStatus}
                                    disabled={loading}
                                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-600 text-white rounded-lg text-sm transition-colors"
                                >
                                    {loading ? 'Checking...' : 'Refresh'}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Dismiss Button */}
                    <button
                        onClick={() => setDismissed(true)}
                        className="text-gray-400 hover:text-white transition-colors"
                        title="Dismiss"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Expanded Details */}
                <AnimatePresence>
                    {expanded && (
                        <motion.div
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                            exit={{ opacity: 0, height: 0 }}
                            className="mt-4 pt-4 border-t border-gray-600"
                        >
                            <h4 className="text-white font-semibold mb-3">Recent Commits on Remote:</h4>
                            <div className="space-y-2">
                                {status.remote_commits.map((commit, i) => (
                                    <div key={i} className="bg-gray-700/50 rounded p-3">
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="font-mono text-xs text-blue-400">{commit.hash}</span>
                                            <span className="text-xs text-gray-500">•</span>
                                            <span className="text-xs text-gray-400">{commit.date}</span>
                                        </div>
                                        <p className="text-white text-sm mb-1">{commit.message}</p>
                                        <p className="text-gray-400 text-xs">by {commit.author}</p>
                                    </div>
                                ))}
                            </div>

                            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-700 rounded">
                                <p className="text-blue-300 text-sm mb-2">
                                    💡 <span className="font-semibold">What to do:</span> Open your terminal and run:
                                </p>
                                <code className="block bg-gray-800 px-3 py-2 rounded text-green-400 font-mono text-sm">
                                    git pull origin main
                                </code>
                                <p className="text-blue-300 text-xs mt-2">
                                    ℹ️ This banner only shows changes - it never pulls automatically to keep your work safe
                                </p>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </motion.div>
        </AnimatePresence>
    )
}
