import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, GitBranch, Trash2, Check, X, Download, Folder, ExternalLink, BarChart3 } from 'lucide-react'
import api from '../utils/axios'
import RepositoryOverview from './RepositoryOverview'

interface Repository {
    id: string
    name: string
    git_url: string
    path: string
    cloned_at: string
    is_active: boolean
    is_local?: boolean  // Local repository (existing project)
    is_clone_to_path?: boolean  // Cloned to specific path
    exists?: boolean
    current_branch?: string
    has_changes?: boolean
}

interface RepositoryManagerProps {
    onRepositoryChange: (repoPath: string) => void
    onShowOverview: () => void
}

export default function RepositoryManager({ onRepositoryChange, onShowOverview }: RepositoryManagerProps) {
    const [repositories, setRepositories] = useState<Record<string, Repository>>({})
    const [isCloning, setIsCloning] = useState(false)
    const [showCloneForm, setShowCloneForm] = useState(false)
    const [showLocalForm, setShowLocalForm] = useState(false)
    const [cloneUrl, setCloneUrl] = useState('')
    const [repoName, setRepoName] = useState('')
    const [cloneToPath, setCloneToPath] = useState('')  // Where to clone the repo
    const [localPath, setLocalPath] = useState('')
    const [localRepoName, setLocalRepoName] = useState('')
    useEffect(() => {
        fetchRepositories()
    }, [])

    const fetchRepositories = async () => {
        try {
            const response = await api.get('/api/repositories')
            if (response.data.success) {
                setRepositories(response.data.repositories)
            }
        } catch (error) {
            console.error('Failed to fetch repositories:', error)
        }
    }

    const handleClone = async () => {
        if (!cloneUrl.trim() || !cloneToPath.trim()) return

        setIsCloning(true)
        try {
            const response = await api.post('/api/clone-to-path', {
                git_url: cloneUrl,
                clone_to_path: cloneToPath,
                name: repoName || undefined
            })

            if (response.data.success) {
                setCloneUrl('')
                setRepoName('')
                setCloneToPath('')
                setShowCloneForm(false)
                await fetchRepositories()
            }
        } catch (error: any) {
            console.error('Clone failed:', error)
            alert(`Clone failed: ${error.response?.data?.detail || error.message}`)
        } finally {
            setIsCloning(false)
        }
    }

    const handleAddLocal = async () => {
        if (!localPath.trim()) return

        setIsCloning(true)
        try {
            const response = await api.post('/api/add-local', {
                local_path: localPath,
                name: localRepoName || undefined
            })

            if (response.data.success) {
                setLocalPath('')
                setLocalRepoName('')
                setShowLocalForm(false)
                await fetchRepositories()
            }
        } catch (error: any) {
            console.error('Add local repository failed:', error)
            alert(`Add local repository failed: ${error.response?.data?.detail || error.message}`)
        } finally {
            setIsCloning(false)
        }
    }

    const handleSetActive = async (repoId: string) => {
        try {
            const response = await api.post('/api/set-active-repo', {
                repo_id: repoId
            })

            if (response.data.success) {
                await fetchRepositories()
                onRepositoryChange(response.data.active_repo.path)
            }
        } catch (error: any) {
            console.error('Failed to set active repository:', error)
            alert(`Failed to set active repository: ${error.response?.data?.detail || error.message}`)
        }
    }

    const handleDelete = async (repoId: string, repoName: string, isLocal: boolean = false) => {
        const confirmMessage = `Are you sure you want to permanently delete "${repoName}"?\n\nThis will:\n• Remove the repository from the list\n• Delete ALL cloned files from your computer\n• Remove the entire folder and its contents\n• This action cannot be undone`

        if (!confirm(confirmMessage)) return

        try {
            const response = await api.delete(`/api/repository/${repoId}`)
            if (response.data.success) {
                await fetchRepositories()
                alert(`✅ Repository "${repoName}" has been completely removed\n\n📁 All files and folders have been deleted from your computer`)
            }
        } catch (error: any) {
            console.error('Failed to delete repository:', error)
            const errorMsg = error.response?.data?.detail || error.message
            alert(`❌ Failed to delete repository: ${errorMsg}`)
        }
    }

    const getRepoDisplayName = (repo: Repository) => {
        return repo.name || repo.git_url.split('/').pop()?.replace('.git', '') || 'Unknown'
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-6 mb-6"
        >
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <Folder className="w-6 h-6 text-purple-400" />
                    <h2 className="text-2xl font-bold">Repository Manager</h2>
                </div>

                <div className="flex items-center gap-2">
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => {
                            setShowCloneForm(!showCloneForm)
                            setShowLocalForm(false)
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors"
                    >
                        <Plus className="w-5 h-5" />
                        Clone & Monitor
                    </motion.button>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => {
                            setShowLocalForm(!showLocalForm)
                            setShowCloneForm(false)
                        }}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg font-medium transition-colors"
                    >
                        <Folder className="w-5 h-5" />
                        Add Local
                    </motion.button>
                </div>
            </div>

            {/* Clone Form */}
            <AnimatePresence>
                {showCloneForm && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mb-6 p-4 bg-black/20 rounded-lg border border-white/10"
                    >
                        <h3 className="text-lg font-semibold mb-4">Clone & Monitor Repository</h3>
                        <p className="text-sm text-gray-400 mb-4">
                            Clone a repository and specify where you'll actually work on it
                        </p>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Git URL *</label>
                                <input
                                    type="text"
                                    value={cloneUrl}
                                    onChange={(e) => setCloneUrl(e.target.value)}
                                    placeholder="https://github.com/username/repository.git"
                                    className="w-full p-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Clone To Path *</label>
                                <input
                                    type="text"
                                    value={cloneToPath}
                                    onChange={(e) => setCloneToPath(e.target.value)}
                                    placeholder="C:\Users\YourName\Projects\my-project"
                                    className="w-full p-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Where to clone and monitor the repository (your actual working directory)
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Repository Name (Optional)</label>
                                <input
                                    type="text"
                                    value={repoName}
                                    onChange={(e) => setRepoName(e.target.value)}
                                    placeholder="my-project"
                                    className="w-full p-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-400"
                                />
                            </div>

                            <div className="flex gap-3">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleClone}
                                    disabled={!cloneUrl.trim() || !cloneToPath.trim() || isCloning}
                                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                                >
                                    {isCloning ? (
                                        <>
                                            <Download className="w-4 h-4 animate-spin" />
                                            Cloning...
                                        </>
                                    ) : (
                                        <>
                                            <Download className="w-4 h-4" />
                                            Clone Repository
                                        </>
                                    )}
                                </motion.button>

                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setShowCloneForm(false)}
                                    className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg font-medium transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                    Cancel
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Add Local Repository Form */}
            <AnimatePresence>
                {showLocalForm && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="mb-6 p-4 bg-black/20 rounded-lg border border-white/10"
                    >
                        <h3 className="text-lg font-semibold mb-4">Add Local Repository</h3>
                        <p className="text-sm text-gray-400 mb-4">
                            Connect to an existing Git repository on your computer
                        </p>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium mb-2">Local Path *</label>
                                <input
                                    type="text"
                                    value={localPath}
                                    onChange={(e) => setLocalPath(e.target.value)}
                                    placeholder="C:\Users\YourName\Projects\my-project"
                                    className="w-full p-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-400"
                                />
                                <p className="text-xs text-gray-500 mt-1">
                                    Full path to your existing Git repository folder
                                </p>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2">Repository Name (Optional)</label>
                                <input
                                    type="text"
                                    value={localRepoName}
                                    onChange={(e) => setLocalRepoName(e.target.value)}
                                    placeholder="my-local-project"
                                    className="w-full p-3 bg-black/30 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-400"
                                />
                            </div>

                            <div className="flex gap-3">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={handleAddLocal}
                                    disabled={!localPath.trim() || isCloning}
                                    className="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
                                >
                                    {isCloning ? (
                                        <>
                                            <Folder className="w-4 h-4 animate-pulse" />
                                            Adding...
                                        </>
                                    ) : (
                                        <>
                                            <Folder className="w-4 h-4" />
                                            Add Repository
                                        </>
                                    )}
                                </motion.button>

                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    onClick={() => setShowLocalForm(false)}
                                    className="flex items-center gap-2 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg font-medium transition-colors"
                                >
                                    <X className="w-4 h-4" />
                                    Cancel
                                </motion.button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Repository List */}
            <div className="space-y-3">
                {Object.keys(repositories).length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                        <Folder className="w-12 h-12 mx-auto mb-4 opacity-50" />
                        <p>No repositories cloned yet</p>
                        <p className="text-sm">Clone a repository to get started</p>
                    </div>
                ) : (
                    Object.values(repositories).map((repo) => (
                        <motion.div
                            key={repo.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className={`p-4 rounded-lg border transition-all ${repo.is_active
                                ? 'bg-purple-500/20 border-purple-500/50'
                                : 'bg-black/20 border-white/10 hover:border-white/20'
                                }`}
                        >
                            <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 flex-wrap mb-2">
                                        <h3 className="font-semibold text-lg">{getRepoDisplayName(repo)}</h3>
                                        {repo.is_active && (
                                            <span className="px-2 py-1 bg-purple-500 text-white text-xs rounded-full">
                                                Active
                                            </span>
                                        )}
                                        {repo.is_local && (
                                            <span className="px-2 py-1 bg-blue-500 text-white text-xs rounded-full">
                                                Local
                                            </span>
                                        )}
                                        {repo.is_clone_to_path && (
                                            <span className="px-2 py-1 bg-green-500 text-white text-xs rounded-full">
                                                Cloned
                                            </span>
                                        )}
                                        {!repo.exists && (
                                            <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">
                                                Missing
                                            </span>
                                        )}
                                    </div>

                                    <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4 text-sm text-gray-400">
                                        <div className="flex items-center gap-1 min-w-0">
                                            <ExternalLink className="w-4 h-4 flex-shrink-0" />
                                            <span className="truncate">{repo.git_url}</span>
                                        </div>

                                        {repo.current_branch && (
                                            <div className="flex items-center gap-1">
                                                <GitBranch className="w-4 h-4" />
                                                <span>{repo.current_branch}</span>
                                            </div>
                                        )}

                                        {repo.has_changes && (
                                            <span className="text-yellow-400">• Changes detected</span>
                                        )}
                                    </div>

                                    <p className="text-xs text-gray-500 mt-1">
                                        Cloned: {new Date(repo.cloned_at).toLocaleDateString()}
                                    </p>
                                </div>

                                <div className="flex items-center gap-2 flex-shrink-0">
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={async () => {
                                            if (!repo.is_active) {
                                                await handleSetActive(repo.id)
                                            }
                                            // Navigate to overview page
                                            setTimeout(() => onShowOverview(), 300)
                                        }}
                                        disabled={!repo.exists}
                                        className={`flex items-center gap-1 px-3 py-1 rounded text-sm font-medium transition-colors ${
                                            !repo.exists
                                                ? 'bg-gray-500 cursor-not-allowed opacity-50'
                                                : 'bg-blue-600 hover:bg-blue-700'
                                        }`}
                                        title="View repository statistics and overview"
                                    >
                                        <BarChart3 className="w-4 h-4" />
                                        Overview
                                    </motion.button>

                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => handleSetActive(repo.id)}
                                        disabled={repo.is_active || !repo.exists}
                                        className={`flex items-center gap-1 px-3 py-1 rounded text-sm font-medium transition-colors ${repo.is_active
                                                ? 'bg-green-500 cursor-default opacity-75'
                                                : !repo.exists
                                                    ? 'bg-gray-500 cursor-not-allowed opacity-50'
                                                    : 'bg-green-600 hover:bg-green-700'
                                            }`}
                                        title={
                                            repo.is_active
                                                ? "Currently active repository"
                                                : !repo.exists
                                                    ? "Repository files missing"
                                                    : "Set as active repository"
                                        }
                                    >
                                        <Check className="w-4 h-4" />
                                        {repo.is_active ? 'Active' : 'Set Active'}
                                    </motion.button>

                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={() => handleDelete(repo.id, getRepoDisplayName(repo), repo.is_local)}
                                        className="flex items-center gap-1 px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm font-medium transition-colors"
                                        title={repo.is_local 
                                            ? "Remove from list (files will remain on your computer)"
                                            : "Permanently delete this repository and all its files"
                                        }
                                    >
                                        <Trash2 className="w-4 h-4" />
                                        {repo.is_local ? 'Remove' : 'Delete'}
                                    </motion.button>
                                </div>
                            </div>
                        </motion.div>
                    ))
                )}
            </div>
        </motion.div>
    )

}