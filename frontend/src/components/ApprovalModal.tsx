import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, X, Edit3, GitCommit, Upload } from 'lucide-react'

interface ApprovalModalProps {
  isOpen: boolean
  type: 'commit' | 'push'
  message: string
  securitySummary?: string
  securityLevel?: string
  onApprove: (editedMessage?: string) => void
  onReject: () => void
  onClose?: () => void
}

export default function ApprovalModal({
  isOpen,
  type,
  message,
  securitySummary,
  securityLevel,
  onApprove,
  onReject,
  onClose
}: ApprovalModalProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editedMessage, setEditedMessage] = useState(message)

  // Debug logging
  console.log('🎭 ApprovalModal render:', { isOpen, type, message })

  const handleClose = () => {
    if (onClose) {
      onClose()
    }
    setIsEditing(false)
  }

  const handleApprove = () => {
    console.log('🔘 Approve button clicked, isEditing:', isEditing, 'editedMessage:', editedMessage)
    onApprove(isEditing ? editedMessage : message)
    setIsEditing(false)
  }

  const handleEdit = () => {
    setIsEditing(true)
    setEditedMessage(message)
  }

  const handleReject = () => {
    console.log('🔘 Reject button clicked')
    onReject()
    setIsEditing(false)
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="glass rounded-2xl p-8 max-w-2xl w-full max-h-[80vh] overflow-y-auto"
          >
            <div className="flex items-center gap-3 mb-6">
              {type === 'commit' ? (
                <GitCommit className="w-8 h-8 text-blue-400" />
              ) : (
                <Upload className="w-8 h-8 text-green-400" />
              )}
              <h2 className="text-2xl font-bold flex-1">
                {type === 'commit' ? 'Commit Approval' : 'Push Approval'}
              </h2>

              {/* Close button */}
              {onClose && (
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={handleClose}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                  title="Close modal"
                >
                  <X className="w-6 h-6 text-gray-400 hover:text-white" />
                </motion.button>
              )}
            </div>

            {type === 'commit' ? (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">
                  AI Generated Commit Message:
                </h3>

                {isEditing ? (
                  <div className="space-y-3">
                    <textarea
                      value={editedMessage}
                      onChange={(e) => setEditedMessage(e.target.value)}
                      className="w-full p-4 bg-black/30 border border-white/20 rounded-lg text-white resize-none focus:outline-none focus:border-blue-400"
                      rows={3}
                      placeholder="Enter your commit message..."
                    />
                    <p className="text-sm text-gray-400">
                      Tip: Use conventional commit format (feat:, fix:, docs:, etc.)
                    </p>
                  </div>
                ) : (
                  <div className="p-4 bg-black/30 border border-white/20 rounded-lg">
                    <code className="text-green-400 text-lg">{message}</code>
                  </div>
                )}
              </div>
            ) : (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3">
                  Ready to push changes to remote repository
                </h3>
                <div className="p-4 bg-black/30 border border-white/20 rounded-lg">
                  <p className="text-gray-300">
                    This will push your committed changes to the remote Git repository.
                  </p>
                  <p className="text-sm text-gray-400 mt-2">
                    Commit message: <code className="text-green-400">{message}</code>
                  </p>
                </div>
              </div>
            )}

            {/* Security Analysis Section */}
            {type === 'commit' && securitySummary && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  🛡️ Security Analysis
                  {securityLevel === 'blocked' && (
                    <span className="px-2 py-1 bg-red-500 text-white text-xs rounded-full">BLOCKED</span>
                  )}
                  {securityLevel === 'critical' && (
                    <span className="px-2 py-1 bg-orange-500 text-white text-xs rounded-full">CRITICAL</span>
                  )}
                  {securityLevel === 'warning' && (
                    <span className="px-2 py-1 bg-yellow-500 text-black text-xs rounded-full">WARNING</span>
                  )}
                  {securityLevel === 'safe' && (
                    <span className="px-2 py-1 bg-green-500 text-white text-xs rounded-full">SAFE</span>
                  )}
                </h3>
                <div className={`p-4 border rounded-lg ${
                  securityLevel === 'blocked' ? 'bg-red-900/20 border-red-500/50' :
                  securityLevel === 'critical' ? 'bg-orange-900/20 border-orange-500/50' :
                  securityLevel === 'warning' ? 'bg-yellow-900/20 border-yellow-500/50' :
                  'bg-green-900/20 border-green-500/50'
                }`}>
                  <pre className="text-sm whitespace-pre-wrap text-gray-300">
                    {securitySummary}
                  </pre>
                </div>
              </div>
            )}

            <div className="flex gap-3 justify-end">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleReject}
                className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 rounded-lg font-medium transition-colors"
              >
                <X className="w-5 h-5" />
                {type === 'commit' ? 'Reject' : 'Cancel Push'}
              </motion.button>

              {type === 'commit' && !isEditing && (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleEdit}
                  className="flex items-center gap-2 px-6 py-3 bg-yellow-600 hover:bg-yellow-700 rounded-lg font-medium transition-colors"
                >
                  <Edit3 className="w-5 h-5" />
                  Edit Message
                </motion.button>
              )}

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleApprove}
                disabled={isEditing && !editedMessage.trim()}
                className="flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg font-medium transition-colors"
              >
                <Check className="w-5 h-5" />
                {isEditing ? 'Save & Approve' : type === 'commit' ? 'Approve Commit' : 'Approve Push'}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}