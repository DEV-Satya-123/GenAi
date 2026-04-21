import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { X, GitBranch, Users, Calendar, FileCode, TrendingUp, Activity } from 'lucide-react'
import axios from '../utils/axios'

interface RepositoryStats {
    total_commits: number
    contributors: Record<string, { name: string; email: string; commits: number }>
    branches: string[]
    current_branch: string
    total_files: number
    languages: Record<string, number>
    first_commit_date: string
    last_commit_date: string
    active_days: number
    commits_by_month: Record<string, number>
    top_contributors: Array<{ name: string; email: string; commits: number }>
}

interface RepositoryOverviewProps {
    onClose: () => void
}

export default function RepositoryOverview({ onClose }: RepositoryOverviewProps) {
    const [stats, setStats] = useState<RepositoryStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchStatistics()
    }, [])

    const fetchStatistics = async () => {
        setLoading(true)
        setError(null)
        try {
            const response = await axios.get('/api/repository-stats')
            if (response.data.success) {
                setStats(response.data)
            } else {
                setError(response.data.error || 'Failed to fetch statistics')
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to fetch repository statistics')
        } finally {
            setLoading(false)
        }
    }

    const getLanguageColor = (ext: string) => {
        const colors: Record<string, string> = {
            '.py': 'bg-blue-500',
            '.js': 'bg-yellow-500',
            '.ts': 'bg-blue-600',
            '.tsx': 'bg-blue-400',
            '.jsx': 'bg-yellow-400',
            '.html': 'bg-orange-500',
            '.css': 'bg-purple-500',
            '.json': 'bg-green-500',
            '.md': 'bg-gray-500',
            '.txt': 'bg-gray-400'
        }
        return colors[ext] || 'bg-gray-600'
    }

    return (
        <div className="min-h-screen py-8">
            <div className="container mx-auto px-4">
                {/* Header */}
                <div className="mb-8 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <Activity className="w-8 h-8 text-purple-400" />
                        <h2 className="text-3xl font-bold">Repository Overview</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors"
                    >
                        <X className="w-5 h-5" />
                        Back to Dashboard
                    </button>
                </div>

                {/* Content */}
                <div>
                    {loading ? (
                        <div className="flex items-center justify-center py-20">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-400"></div>
                        </div>
                    ) : error ? (
                        <div className="text-center py-20">
                            <p className="text-red-400 text-lg">{error}</p>
                            <button
                                onClick={fetchStatistics}
                                className="mt-4 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg"
                            >
                                Retry
                            </button>
                        </div>
                    ) : stats ? (
                        <div className="space-y-6">
                            {/* Key Metrics */}
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                <div className="bg-gradient-to-br from-purple-500/20 to-purple-600/20 border border-purple-500/30 rounded-xl p-6">
                                    <div className="flex items-center gap-3 mb-2">
                                        <GitBranch className="w-6 h-6 text-purple-400" />
                                        <h3 className="text-sm font-medium text-gray-400">Total Commits</h3>
                                    </div>
                                    <p className="text-4xl font-bold text-purple-400">{stats.total_commits}</p>
                                </div>

                                <div className="bg-gradient-to-br from-blue-500/20 to-blue-600/20 border border-blue-500/30 rounded-xl p-6">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Users className="w-6 h-6 text-blue-400" />
                                        <h3 className="text-sm font-medium text-gray-400">Contributors</h3>
                                    </div>
                                    <p className="text-4xl font-bold text-blue-400">{Object.keys(stats.contributors).length}</p>
                                </div>

                                <div className="bg-gradient-to-br from-green-500/20 to-green-600/20 border border-green-500/30 rounded-xl p-6">
                                    <div className="flex items-center gap-3 mb-2">
                                        <Calendar className="w-6 h-6 text-green-400" />
                                        <h3 className="text-sm font-medium text-gray-400">Active Days</h3>
                                    </div>
                                    <p className="text-4xl font-bold text-green-400">{stats.active_days}</p>
                                </div>

                                <div className="bg-gradient-to-br from-orange-500/20 to-orange-600/20 border border-orange-500/30 rounded-xl p-6">
                                    <div className="flex items-center gap-3 mb-2">
                                        <FileCode className="w-6 h-6 text-orange-400" />
                                        <h3 className="text-sm font-medium text-gray-400">Total Files</h3>
                                    </div>
                                    <p className="text-4xl font-bold text-orange-400">{stats.total_files}</p>
                                </div>
                            </div>

                            {/* Repository Info */}
                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Branch Info */}
                                <div className="bg-black/30 border border-white/10 rounded-xl p-6">
                                    <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                        <GitBranch className="w-5 h-5 text-purple-400" />
                                        Branches
                                    </h3>
                                    <div className="space-y-2">
                                        <p className="text-gray-400">
                                            Current: <span className="text-white font-semibold">{stats.current_branch}</span>
                                        </p>
                                        <p className="text-gray-400">
                                            Total: <span className="text-white font-semibold">{stats.branches.length}</span>
                                        </p>
                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {stats.branches.slice(0, 5).map((branch) => (
                                                <span
                                                    key={branch}
                                                    className={`px-3 py-1 rounded-full text-sm ${branch === stats.current_branch
                                                        ? 'bg-purple-500 text-white'
                                                        : 'bg-gray-700 text-gray-300'
                                                        }`}
                                                >
                                                    {branch}
                                                </span>
                                            ))}
                                            {stats.branches.length > 5 && (
                                                <span className="px-3 py-1 bg-gray-700 text-gray-400 rounded-full text-sm">
                                                    +{stats.branches.length - 5} more
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>

                                {/* Timeline */}
                                <div className="bg-black/30 border border-white/10 rounded-xl p-6">
                                    <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                        <Calendar className="w-5 h-5 text-green-400" />
                                        Timeline
                                    </h3>
                                    <div className="space-y-3">
                                        <div>
                                            <p className="text-sm text-gray-400">First Commit</p>
                                            <p className="text-lg font-semibold text-white">{stats.first_commit_date}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-400">Last Commit</p>
                                            <p className="text-lg font-semibold text-white">{stats.last_commit_date}</p>
                                        </div>
                                        <div>
                                            <p className="text-sm text-gray-400">Active Days</p>
                                            <p className="text-lg font-semibold text-green-400">{stats.active_days} days</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Top Contributors */}
                            <div className="bg-black/30 border border-white/10 rounded-xl p-6">
                                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                    <Users className="w-5 h-5 text-blue-400" />
                                    Top Contributors
                                </h3>
                                <div className="space-y-3">
                                    {stats.top_contributors.map((contributor, index) => (
                                        <div
                                            key={contributor.email}
                                            className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                                        >
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-bold">
                                                    {index + 1}
                                                </div>
                                                <div>
                                                    <p className="font-semibold text-white">{contributor.name}</p>
                                                    <p className="text-sm text-gray-400">{contributor.email}</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-2xl font-bold text-purple-400">{contributor.commits}</p>
                                                <p className="text-xs text-gray-400">commits</p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Languages */}
                            <div className="bg-black/30 border border-white/10 rounded-xl p-6">
                                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                    <FileCode className="w-5 h-5 text-orange-400" />
                                    File Types
                                </h3>
                                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
                                    {Object.entries(stats.languages).map(([ext, count]) => (
                                        <div
                                            key={ext}
                                            className="bg-gray-800/50 rounded-lg p-4 text-center"
                                        >
                                            <div className={`w-12 h-12 ${getLanguageColor(ext)} rounded-lg mx-auto mb-2 flex items-center justify-center text-white font-bold`}>
                                                {ext}
                                            </div>
                                            <p className="text-2xl font-bold text-white">{count}</p>
                                            <p className="text-xs text-gray-400">files</p>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Commit Activity by Month */}
                            <div className="bg-black/30 border border-white/10 rounded-xl p-6">
                                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                                    <TrendingUp className="w-5 h-5 text-green-400" />
                                    Commit Activity (Last 12 Months)
                                </h3>
                                <div className="space-y-2">
                                    {Object.entries(stats.commits_by_month)
                                        .sort((a, b) => b[0].localeCompare(a[0]))
                                        .slice(0, 12)
                                        .map(([month, count]) => {
                                            const maxCommits = Math.max(...Object.values(stats.commits_by_month))
                                            const percentage = (count / maxCommits) * 100
                                            return (
                                                <div key={month} className="flex items-center gap-3">
                                                    <span className="text-sm text-gray-400 w-20">{month}</span>
                                                    <div className="flex-1 bg-gray-800 rounded-full h-6 overflow-hidden">
                                                        <div
                                                            className="bg-gradient-to-r from-purple-500 to-blue-500 h-full flex items-center justify-end pr-2"
                                                            style={{ width: `${percentage}%` }}
                                                        >
                                                            <span className="text-xs font-semibold text-white">{count}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            )
                                        })}
                                </div>
                            </div>
                        </div>
                    ) : null}
                </div>
            </div>
        </div>
    )
}
