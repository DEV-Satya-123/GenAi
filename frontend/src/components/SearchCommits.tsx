import { useState } from 'react'
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

export default function SearchCommits() {
    const [query, setQuery] = useState('')
    const [results, setResults] = useState<Commit[]>([])
    const [loading, setLoading] = useState(false)
    const [searched, setSearched] = useState(false)
    const [searchType, setSearchType] = useState<'message' | 'author' | 'all'>('all')
    const [maxResults, setMaxResults] = useState(10)
    const [expandedCommit, setExpandedCommit] = useState<string | null>(null)

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!query.trim()) return

        setLoading(true)
        setSearched(true)

        try {
            const response = await axios.get(`/api/search-commits?query=${encodeURIComponent(query)}&max_results=${maxResults}`)
            setResults(response.data.results || [])
        } catch (error) {
            console.error('Search failed:', error)
            setResults([])
        } finally {
            setLoading(false)
        }
    }

    const copyHash = (hash: string) => {
        navigator.clipboard.writeText(hash)
        // Show toast notification
        const toast = document.createElement('div')
        toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50'
        toast.textContent = `Copied: ${hash}`
        document.body.appendChild(toast)
        setTimeout(() => toast.remove(), 2000)
    }

    const getCommitTypeColor = (message: string) => {
        const lowerMessage = message.toLowerCase()
        if (lowerMessage.startsWith('feat')) return 'text-green-400 border-green-500'
        if (lowerMessage.startsWith('fix')) return 'text-red-400 border-red-500'
        if (lowerMessage.startsWith('docs')) return 'text-blue-400 border-blue-500'
        if (lowerMessage.startsWith('style')) return 'text-purple-400 border-purple-500'
        if (lowerMessage.startsWith('refactor')) return 'text-yellow-400 border-yellow-500'
        if (lowerMessage.startsWith('test')) return 'text-pink-400 border-pink-500'
        if (lowerMessage.startsWith('chore')) return 'text-gray-400 border-gray-500'
        return 'text-white border-gray-500'
    }

    const getCommitTypeIcon = (message: string) => {
        const lowerMessage = message.toLowerCase()

        if (lowerMessage.startsWith('feat')) {
            return '✨'
        } else if (lowerMessage.startsWith('fix')) {
            return '🐛'
        } else if (lowerMessage.startsWith('docs')) {
            return '📝'
        } else if (lowerMessage.startsWith('style')) {
            return '💄'
        } else if (lowerMessage.startsWith('refactor')) {
            return '♻️'
        } else if (lowerMessage.startsWith('test')) {
            return '✅'
        } else if (lowerMessage.startsWith('chore')) {
            return '🔧'
        }
        return '📦'
    }

    const highlightQuery = (text: string) => {
        if (!query) return text
        const parts = text.split(new RegExp(`(${query})`, 'gi'))
        return parts.map((part, i) =>
            part.toLowerCase() === query.toLowerCase()
                ? <mark key={i} className="bg-yellow-500/30 text-yellow-300 px-1 rounded">{part}</mark>
                : part
        )
    }

    const quickSearches = [
        { label: 'Features', query: 'feat', icon: '✨' },
        { label: 'Bug Fixes', query: 'fix', icon: '🐛' },
        { label: 'Documentation', query: 'docs', icon: '📝' },
        { label: 'Refactoring', query: 'refactor', icon: '♻️' },
    ]

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-gray-800 rounded-lg p-6 shadow-xl border border-gray-700"
        >
            <div className="flex items-center gap-3 mb-6">
                <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <h2 className="text-2xl font-bold text-white">Search Commits</h2>
            </div>

            {/* Search Form */}
            <form onSubmit={handleSearch} className="mb-6 space-y-4">
                <div className="flex gap-2">
                    <div className="flex-1 relative">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search by message, author, or content..."
                            className="w-full px-4 py-3 pl-10 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <svg className="w-5 h-5 text-gray-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                    </div>

                    <select
                        value={maxResults}
                        onChange={(e) => setMaxResults(Number(e.target.value))}
                        className="px-4 py-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value={5}>Top 5</option>
                        <option value={10}>Top 10</option>
                        <option value={20}>Top 20</option>
                        <option value={50}>Top 50</option>
                    </select>

                    <button
                        type="submit"
                        disabled={loading || !query.trim()}
                        className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors flex items-center gap-2"
                    >
                        {loading ? (
                            <>
                                <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Searching...
                            </>
                        ) : (
                            <>
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                                Search
                            </>
                        )}
                    </button>
                </div>

                {/* Quick Search Buttons */}
                <div className="flex flex-wrap gap-2">
                    <span className="text-sm text-gray-400 self-center">Quick search:</span>
                    {quickSearches.map((qs) => (
                        <button
                            key={qs.query}
                            type="button"
                            onClick={() => {
                                setQuery(qs.query)
                                setSearched(false)
                            }}
                            className="px-3 py-1.5 bg-gray-700 hover:bg-gray-600 text-white text-sm rounded-lg transition-colors flex items-center gap-1.5"
                        >
                            <span>{qs.icon}</span>
                            <span>{qs.label}</span>
                        </button>
                    ))}
                </div>
            </form>

            {/* Loading State */}
            {loading && (
                <div className="text-center py-8">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    <p className="text-gray-400 mt-2">Searching commits...</p>
                </div>
            )}

            {/* Empty State */}
            {!loading && searched && results.length === 0 && (
                <div className="text-center py-8">
                    <svg className="w-16 h-16 text-gray-600 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <p className="text-gray-400 text-lg mb-2">No commits found for "{query}"</p>
                    <p className="text-gray-500 text-sm">Try a different search term or check your repository</p>
                </div>
            )}

            {/* Results */}
            {!loading && results.length > 0 && (
                <div className="space-y-3">
                    <div className="flex items-center justify-between mb-4">
                        <p className="text-sm text-gray-400">
                            Found <span className="text-white font-semibold">{results.length}</span> commit{results.length !== 1 ? 's' : ''} matching "{query}"
                        </p>
                        <button
                            onClick={() => {
                                setQuery('')
                                setResults([])
                                setSearched(false)
                            }}
                            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                        >
                            Clear results
                        </button>
                    </div>

                    {results.map((commit, index) => (
                        <motion.div
                            key={commit.full_hash}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className={`bg-gray-700 rounded-lg p-4 hover:bg-gray-650 transition-all border-l-4 ${getCommitTypeColor(commit.message).split(' ')[1]}`}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    {/* Header */}
                                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                                        <span className="text-2xl">{getCommitTypeIcon(commit.message)}</span>
                                        <button
                                            onClick={() => copyHash(commit.hash)}
                                            className="font-mono text-sm px-2 py-1 bg-gray-800 hover:bg-gray-900 text-blue-400 hover:text-blue-300 rounded transition-colors"
                                            title="Click to copy full hash"
                                        >
                                            {commit.hash}
                                        </button>
                                        <span className="text-xs text-gray-500">•</span>
                                        <span className="text-xs text-gray-400">{commit.date}</span>
                                    </div>

                                    {/* Commit Message */}
                                    <p className={`font-medium mb-2 break-words ${getCommitTypeColor(commit.message).split(' ')[0]}`}>
                                        {highlightQuery(commit.message)}
                                    </p>

                                    {/* Footer */}
                                    <div className="flex items-center gap-4 text-sm text-gray-400">
                                        <span className="flex items-center gap-1.5">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                            </svg>
                                            {highlightQuery(commit.author)}
                                        </span>
                                        <span className="flex items-center gap-1.5">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                            </svg>
                                            {commit.files_changed} file{commit.files_changed !== 1 ? 's' : ''}
                                        </span>

                                        {/* Expand Button */}
                                        <button
                                            onClick={() => setExpandedCommit(expandedCommit === commit.hash ? null : commit.hash)}
                                            className="ml-auto text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                                        >
                                            {expandedCommit === commit.hash ? (
                                                <>
                                                    <span className="text-xs">Hide details</span>
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                                    </svg>
                                                </>
                                            ) : (
                                                <>
                                                    <span className="text-xs">Show details</span>
                                                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                                    </svg>
                                                </>
                                            )}
                                        </button>
                                    </div>

                                    {/* Expanded Details */}
                                    {expandedCommit === commit.hash && (
                                        <motion.div
                                            initial={{ opacity: 0, height: 0 }}
                                            animate={{ opacity: 1, height: 'auto' }}
                                            exit={{ opacity: 0, height: 0 }}
                                            className="mt-4 pt-4 border-t border-gray-600"
                                        >
                                            <div className="space-y-2 text-sm">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-gray-400">Full hash:</span>
                                                    <code className="text-xs bg-gray-800 px-2 py-1 rounded text-gray-300 font-mono">
                                                        {commit.full_hash}
                                                    </code>
                                                    <button
                                                        onClick={() => copyHash(commit.full_hash)}
                                                        className="text-blue-400 hover:text-blue-300"
                                                        title="Copy full hash"
                                                    >
                                                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                                        </svg>
                                                    </button>
                                                </div>
                                                <div className="flex gap-2">
                                                    <button
                                                        onClick={() => copyHash(`git show ${commit.hash}`)}
                                                        className="px-3 py-1.5 bg-gray-800 hover:bg-gray-900 text-gray-300 rounded text-xs transition-colors"
                                                    >
                                                        📋 Copy git show command
                                                    </button>
                                                    <button
                                                        onClick={() => copyHash(`git checkout ${commit.hash}`)}
                                                        className="px-3 py-1.5 bg-gray-800 hover:bg-gray-900 text-gray-300 rounded text-xs transition-colors"
                                                    >
                                                        🔄 Copy git checkout command
                                                    </button>
                                                </div>
                                            </div>
                                        </motion.div>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            )}
        </motion.div>
    )
}
