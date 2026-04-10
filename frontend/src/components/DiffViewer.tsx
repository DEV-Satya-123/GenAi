import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface DiffViewerProps {
  diff: string
  files?: string[]
  stats?: {
    additions: number
    deletions: number
    filesChanged: number
  }
}

export default function DiffViewer({ diff, files = [], stats }: DiffViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)

  // Parse diff to extract file changes
  const parseDiff = (diffText: string) => {
    const lines = diffText.split('\n')
    const fileChanges: { [key: string]: { additions: number; deletions: number; lines: string[] } } = {}
    let currentFile = ''
    
    lines.forEach(line => {
      // Detect file headers
      if (line.startsWith('diff --git') || line.startsWith('+++')) {
        const match = line.match(/b\/(.+)$/)
        if (match) {
          currentFile = match[1]
          if (!fileChanges[currentFile]) {
            fileChanges[currentFile] = { additions: 0, deletions: 0, lines: [] }
          }
        }
      } else if (currentFile) {
        fileChanges[currentFile].lines.push(line)
        
        // Count additions and deletions
        if (line.startsWith('+') && !line.startsWith('+++')) {
          fileChanges[currentFile].additions++
        } else if (line.startsWith('-') && !line.startsWith('---')) {
          fileChanges[currentFile].deletions++
        }
      }
    })
    
    return fileChanges
  }

  const fileChanges = parseDiff(diff)
  const fileList = Object.keys(fileChanges).length > 0 ? Object.keys(fileChanges) : files

  const getLineColor = (line: string) => {
    if (line.startsWith('+') && !line.startsWith('+++')) return 'text-green-400 bg-green-900/20'
    if (line.startsWith('-') && !line.startsWith('---')) return 'text-red-400 bg-red-900/20'
    if (line.startsWith('@@')) return 'text-blue-400 bg-blue-900/20'
    if (line.startsWith('diff') || line.startsWith('index') || line.startsWith('---') || line.startsWith('+++')) {
      return 'text-gray-500'
    }
    return 'text-gray-300'
  }

  const getFileIcon = (filename: string) => {
    const ext = filename.split('.').pop()?.toLowerCase()
    
    if (['js', 'jsx', 'ts', 'tsx'].includes(ext || '')) {
      return '📜'
    } else if (['py'].includes(ext || '')) {
      return '🐍'
    } else if (['json'].includes(ext || '')) {
      return '📋'
    } else if (['md'].includes(ext || '')) {
      return '📝'
    } else if (['css', 'scss'].includes(ext || '')) {
      return '🎨'
    } else if (['html'].includes(ext || '')) {
      return '🌐'
    }
    return '📄'
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Summary Header */}
      <div className="p-4 bg-gray-750 border-b border-gray-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-white font-semibold">
                {stats?.filesChanged || fileList.length} file{(stats?.filesChanged || fileList.length) !== 1 ? 's' : ''} changed
              </span>
            </div>
            
            {stats && (
              <div className="flex items-center gap-3 text-sm">
                <span className="text-green-400 flex items-center gap-1">
                  <span className="font-mono">+{stats.additions}</span>
                  <span className="text-gray-500">additions</span>
                </span>
                <span className="text-red-400 flex items-center gap-1">
                  <span className="font-mono">-{stats.deletions}</span>
                  <span className="text-gray-500">deletions</span>
                </span>
              </div>
            )}
          </div>
          
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
          >
            {isExpanded ? (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                </svg>
                Hide Details
              </>
            ) : (
              <>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
                View Details
              </>
            )}
          </button>
        </div>
      </div>

      {/* Expanded Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
          >
            {/* File List */}
            <div className="border-b border-gray-700">
              <div className="p-4 bg-gray-750">
                <h3 className="text-sm font-semibold text-gray-400 mb-3">Modified Files</h3>
                <div className="space-y-2">
                  {fileList.map((file, index) => {
                    const fileStats = fileChanges[file]
                    return (
                      <button
                        key={index}
                        onClick={() => setSelectedFile(selectedFile === file ? null : file)}
                        className={`w-full text-left px-3 py-2 rounded-lg transition-colors ${
                          selectedFile === file
                            ? 'bg-blue-900/30 border border-blue-700'
                            : 'bg-gray-700 hover:bg-gray-650 border border-gray-600'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 flex-1 min-w-0">
                            <span className="text-xl">{getFileIcon(file)}</span>
                            <span className="text-white font-mono text-sm truncate">{file}</span>
                          </div>
                          
                          {fileStats && (
                            <div className="flex items-center gap-2 text-xs ml-2">
                              {fileStats.additions > 0 && (
                                <span className="text-green-400">+{fileStats.additions}</span>
                              )}
                              {fileStats.deletions > 0 && (
                                <span className="text-red-400">-{fileStats.deletions}</span>
                              )}
                            </div>
                          )}
                        </div>
                      </button>
                    )
                  })}
                </div>
              </div>
            </div>

            {/* Diff Content */}
            <div className="p-4 bg-gray-900">
              {selectedFile ? (
                // Show specific file diff
                <div>
                  <div className="flex items-center gap-2 mb-3 pb-2 border-b border-gray-700">
                    <span className="text-xl">{getFileIcon(selectedFile)}</span>
                    <span className="text-white font-mono text-sm">{selectedFile}</span>
                  </div>
                  <div className="bg-gray-950 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-xs font-mono">
                      {fileChanges[selectedFile]?.lines.map((line, i) => (
                        <div key={i} className={`${getLineColor(line)} px-2 py-0.5`}>
                          {line || ' '}
                        </div>
                      ))}
                    </pre>
                  </div>
                </div>
              ) : (
                // Show full diff
                <div>
                  <h3 className="text-sm font-semibold text-gray-400 mb-3">Full Diff</h3>
                  <div className="bg-gray-950 rounded-lg p-4 overflow-x-auto max-h-96 overflow-y-auto">
                    <pre className="text-xs font-mono">
                      {diff.split('\n').map((line, i) => (
                        <div key={i} className={`${getLineColor(line)} px-2 py-0.5`}>
                          {line || ' '}
                        </div>
                      ))}
                    </pre>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
