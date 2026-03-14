import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Play, Square, GitCommit, Activity } from 'lucide-react'
import axios from 'axios'
import ApprovalModal from './ApprovalModal'

interface DashboardProps {
    onRunStart: () => void
    onRunEnd: () => void
}

export default function Dashboard({ onRunStart, onRunEnd }: DashboardProps) {
    const [isRunning, setIsRunning] = useState(false)
    const [logs, setLogs] = useState<string[]>([])
    const [socket, setSocket] = useState<any>(null)
    const [approvalModal, setApprovalModal] = useState<{
        isOpen: boolean
        type: 'commit' | 'push'
        message: string
        data?: any
    }>({
        isOpen: false,
        type: 'commit',
        message: ''
    })

    useEffect(() => {
        // Initialize WebSocket connection with retry logic
        let ws: WebSocket | null = null
        let reconnectTimeout: number
        let isComponentMounted = true

        const connectWebSocket = () => {
            if (!isComponentMounted) return

            try {
                ws = new WebSocket('ws://localhost:8000/ws')

                ws.onopen = () => {
                    console.log('✅ WebSocket connected')
                    setSocket(ws)
                }

                ws.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data)
                        handleWebSocketMessage(data)
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error)
                    }
                }

                ws.onclose = (event) => {
                    if (event.wasClean) {
                        console.log('WebSocket closed cleanly')
                    } else {
                        console.log('WebSocket disconnected unexpectedly')
                    }
                    setSocket(null)
                    // Only retry if component is still mounted and it wasn't a clean close
                    if (isComponentMounted && !event.wasClean) {
                        reconnectTimeout = window.setTimeout(connectWebSocket, 3000)
                    }
                }

                ws.onerror = (error) => {
                    console.log('WebSocket connection failed, retrying...')
                    setSocket(null)
                }
            } catch (error) {
                console.error('Failed to create WebSocket:', error)
                // Retry connection after 5 seconds
                if (isComponentMounted) {
                    reconnectTimeout = window.setTimeout(connectWebSocket, 5000)
                }
            }
        }

        connectWebSocket()

        return () => {
            isComponentMounted = false
            if (reconnectTimeout) {
                window.clearTimeout(reconnectTimeout)
            }
            if (ws) {
                ws.close(1000, 'Component unmounting')
            }
        }
    }, [])

    const handleWebSocketMessage = (data: any) => {
        switch (data.type) {
            case 'workflow_started':
                addLog(`🚀 ${data.message}`)
                break
            case 'workflow_paused':
                addLog(`⏸️ ${data.message}`)
                // Show approval modal when workflow pauses
                if (data.approval_data) {
                    setApprovalModal({
                        isOpen: true,
                        type: data.approval_data.type === 'push_approval' ? 'push' : 'commit',
                        message: data.approval_data.commit_message || 'Approval needed',
                        data: data.approval_data
                    })
                }
                break
            case 'step_update':
                addLog(`🔄 ${data.message}`)
                break
            case 'step_complete':
                addLog(`✅ ${data.message}`)
                break
            case 'step_error':
                addLog(`❌ ${data.message}`)
                break
            case 'approval_required':
                console.log('🔔 Approval required received:', data)
                console.log('🔔 Approval type:', data.approval_type)
                console.log('🔔 Data:', data.data)

                const modalType = data.approval_type === 'push_approval' ? 'push' : 'commit'
                console.log('🔔 Setting modal type to:', modalType)

                setApprovalModal({
                    isOpen: true,
                    type: modalType,
                    message: data.data.commit_message || 'Approval needed',
                    data: data.data
                })
                addLog(`⏸️ Approval required: ${data.data.commit_message || 'Waiting for approval'}`)
                break
            case 'workflow_complete':
                addLog(`🎉 ${data.message}`)
                if (data.result) {
                    addLog(`📋 Commit: ${data.result.commit_message}`)
                    addLog(`✅ Committed: ${data.result.committed}`)
                    addLog(`🚀 Pushed: ${data.result.pushed}`)
                }
                setIsRunning(false)
                onRunEnd()
                break
            case 'workflow_error':
                addLog(`💥 ${data.message}`)
                setIsRunning(false)
                onRunEnd()
                break
            case 'pong':
                // Handle ping/pong for connection health
                break
            default:
                console.log('WebSocket message:', data)
        }
    }

    const handleRun = async () => {
        setIsRunning(true)
        onRunStart()
        setLogs([])

        try {
            addLog('🚀 Starting AI Git Automation Agent...')

            const response = await axios.post('/api/run')

            if (response.data.success) {
                addLog('✅ Agent execution completed successfully')
            } else {
                addLog('❌ Agent execution failed')
            }
        } catch (error: any) {
            addLog(`❌ Error: ${error.message}`)
            setIsRunning(false)
            onRunEnd()
        }
    }

    const handleApproval = async (approved: boolean, editedMessage?: string) => {
        const approvalData = {
            action: approved ? 'approve' : 'reject',
            commit_message: editedMessage || approvalModal.message,
            approval_type: approvalModal.type
        }

        console.log('📤 Sending approval data:', approvalData)

        try {
            // Send approval via new API endpoint
            const response = await axios.post('/api/approve', approvalData)
            console.log('📥 Approval response:', response.data)

            addLog(`✅ ${approvalModal.type === 'commit' ? 'Commit' : 'Push'} ${approved ? 'approved' : 'rejected'}`)
        } catch (error: any) {
            console.error('❌ Approval error:', error)
            addLog(`❌ Error sending approval: ${error.message}`)
        }

        // Close the modal
        setApprovalModal({ ...approvalModal, isOpen: false })
    }

    const addLog = (message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`])
    }

    return (
        <>
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="glass rounded-2xl p-6"
            >
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <Activity className="w-6 h-6 text-blue-400" />
                        <h2 className="text-2xl font-bold">Control Panel</h2>
                        {socket && (
                            <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 border border-green-500/50 rounded-full text-sm">
                                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                                Connected
                            </div>
                        )}
                    </div>

                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={handleRun}
                        disabled={isRunning || !socket}
                        className={`flex items-center gap-2 px-6 py-3 rounded-lg font-medium transition-all ${isRunning || !socket
                            ? 'bg-gray-600 cursor-not-allowed'
                            : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700'
                            }`}
                    >
                        {isRunning ? (
                            <>
                                <Square className="w-5 h-5" />
                                Running...
                            </>
                        ) : (
                            <>
                                <Play className="w-5 h-5" />
                                Run Agent
                            </>
                        )}
                    </motion.button>

                    {/* Test button to manually trigger approval modal */}
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setApprovalModal({
                            isOpen: true,
                            type: 'commit',
                            message: 'feat: test commit message',
                            data: {}
                        })}
                        className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-medium transition-colors text-sm"
                    >
                        Test Modal
                    </motion.button>
                </div>

                <div className="space-y-4">
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                        <GitCommit className="w-4 h-4" />
                        <span>Execution Logs</span>
                    </div>

                    <div className="bg-black/30 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                        {logs.length === 0 ? (
                            <p className="text-gray-500">No logs yet. Run the agent to see output.</p>
                        ) : (
                            logs.map((log, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    className="text-gray-300 mb-1"
                                >
                                    {log}
                                </motion.div>
                            ))
                        )}
                    </div>
                </div>
            </motion.div>

            <ApprovalModal
                isOpen={approvalModal.isOpen}
                type={approvalModal.type}
                message={approvalModal.message}
                onApprove={(editedMessage) => handleApproval(true, editedMessage)}
                onReject={() => handleApproval(false)}
                onClose={() => setApprovalModal({ ...approvalModal, isOpen: false })}
            />
        </>
    )
}
