import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { GitBranch, FileText, CheckCircle, XCircle } from 'lucide-react'
import axios from 'axios'

interface Status {
  has_changes: boolean
  current_branch: string
  repo_path: string
}

export default function StatusCard() {
  const [status, setStatus] = useState<Status | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await axios.get('/api/status')
      setStatus(response.data)
      setLoading(false)
    } catch (error) {
      console.error('Failed to fetch status:', error)
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="glass rounded-2xl p-6 animate-pulse">
        <div className="h-20 bg-white/10 rounded"></div>
      </div>
    )
  }

  return (
    <>
      <motion.div
        whileHover={{ scale: 1.02 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-2">
          <GitBranch className="w-5 h-5 text-blue-400" />
          <h3 className="text-sm font-medium text-gray-400">Current Branch</h3>
        </div>
        <p className="text-2xl font-bold">{status?.current_branch || 'N/A'}</p>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.02 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-2">
          <FileText className="w-5 h-5 text-purple-400" />
          <h3 className="text-sm font-medium text-gray-400">Changes</h3>
        </div>
        <div className="flex items-center gap-2">
          {status?.has_changes ? (
            <>
              <CheckCircle className="w-6 h-6 text-green-400" />
              <p className="text-2xl font-bold">Detected</p>
            </>
          ) : (
            <>
              <XCircle className="w-6 h-6 text-gray-400" />
              <p className="text-2xl font-bold">None</p>
            </>
          )}
        </div>
      </motion.div>

      <motion.div
        whileHover={{ scale: 1.02 }}
        className="glass rounded-2xl p-6"
      >
        <div className="flex items-center gap-3 mb-2">
          <FileText className="w-5 h-5 text-green-400" />
          <h3 className="text-sm font-medium text-gray-400">Repository</h3>
        </div>
        <p className="text-lg font-mono truncate">{status?.repo_path || 'N/A'}</p>
      </motion.div>
    </>
  )
}
