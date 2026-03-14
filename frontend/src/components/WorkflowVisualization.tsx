import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, FileText, Bot, Clock, GitCommit, Upload, CheckCircle } from 'lucide-react'

interface WorkflowStep {
    id: string
    name: string
    icon: any
    position: { x: number; y: number; z: number }
    color: string
    glowColor: string
}

interface WorkflowVisualizationProps {
    currentStep: string
    isRunning: boolean
}

const workflowSteps: WorkflowStep[] = [
    {
        id: 'detecting',
        name: 'Detecting Changes',
        icon: Search,
        position: { x: -200, y: 0, z: 0 },
        color: 'from-blue-500 to-cyan-500',
        glowColor: 'shadow-blue-500/50'
    },
    {
        id: 'analyzing',
        name: 'Analyzing Diff',
        icon: FileText,
        position: { x: -100, y: -50, z: 30 },
        color: 'from-purple-500 to-pink-500',
        glowColor: 'shadow-purple-500/50'
    },
    {
        id: 'generating',
        name: 'AI Generating Message',
        icon: Bot,
        position: { x: 0, y: 0, z: 60 },
        color: 'from-green-500 to-emerald-500',
        glowColor: 'shadow-green-500/50'
    },
    {
        id: 'commit_approval',
        name: 'Awaiting Commit Approval',
        icon: Clock,
        position: { x: 100, y: 50, z: 30 },
        color: 'from-yellow-500 to-orange-500',
        glowColor: 'shadow-yellow-500/50'
    },
    {
        id: 'committing',
        name: 'Committing Changes',
        icon: GitCommit,
        position: { x: 200, y: 0, z: 0 },
        color: 'from-indigo-500 to-blue-500',
        glowColor: 'shadow-indigo-500/50'
    },
    {
        id: 'push_approval',
        name: 'Awaiting Push Approval',
        icon: Clock,
        position: { x: 300, y: -50, z: -30 },
        color: 'from-pink-500 to-rose-500',
        glowColor: 'shadow-pink-500/50'
    },
    {
        id: 'pushing',
        name: 'Pushing to Remote',
        icon: Upload,
        position: { x: 400, y: 0, z: 0 },
        color: 'from-emerald-500 to-teal-500',
        glowColor: 'shadow-emerald-500/50'
    },
    {
        id: 'complete',
        name: 'Complete',
        icon: CheckCircle,
        position: { x: 500, y: 50, z: 30 },
        color: 'from-green-600 to-lime-500',
        glowColor: 'shadow-green-600/50'
    }
]

export default function WorkflowVisualization({ currentStep, isRunning }: WorkflowVisualizationProps) {
    const [activeStepIndex, setActiveStepIndex] = useState(0)
    const [cameraRotation, setCameraRotation] = useState({ x: 0, y: 0 })
    const [particlePositions, setParticlePositions] = useState<Array<{ x: number, y: number, z: number }>>([])

    // Auto-rotate camera for 3D effect
    useEffect(() => {
        if (!isRunning) return

        const interval = setInterval(() => {
            setCameraRotation(prev => ({
                x: prev.x + 0.5,
                y: prev.y + 0.3
            }))
        }, 100)

        return () => clearInterval(interval)
    }, [isRunning])

    // Update active step based on current step
    useEffect(() => {
        const stepIndex = workflowSteps.findIndex(step => step.id === currentStep)
        if (stepIndex !== -1) {
            setActiveStepIndex(stepIndex)
        }
    }, [currentStep])

    // Generate floating particles
    useEffect(() => {
        const particles = Array.from({ length: 20 }, (_, i) => ({
            x: Math.random() * 800 - 400,
            y: Math.random() * 400 - 200,
            z: Math.random() * 200 - 100
        }))
        setParticlePositions(particles)
    }, [])

    const getCurrentStepPosition = () => {
        const currentStepData = workflowSteps[activeStepIndex]
        return currentStepData ? currentStepData.position : { x: 0, y: 0, z: 0 }
    }

    const cameraTransform = `
    perspective(1000px) 
    rotateX(${cameraRotation.x}deg) 
    rotateY(${cameraRotation.y}deg)
    translateZ(-200px)
  `

    return (
        <div className="relative w-full h-96 overflow-hidden bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 rounded-2xl">
            {/* 3D Scene Container */}
            <div
                className="absolute inset-0 flex items-center justify-center"
                style={{
                    transform: cameraTransform,
                    transformStyle: 'preserve-3d'
                }}
            >
                {/* Floating Particles */}
                {particlePositions.map((particle, index) => (
                    <motion.div
                        key={index}
                        className="absolute w-1 h-1 bg-white/30 rounded-full"
                        style={{
                            transform: `translate3d(${particle.x}px, ${particle.y}px, ${particle.z}px)`,
                        }}
                        animate={{
                            y: [particle.y, particle.y - 20, particle.y],
                            opacity: [0.3, 0.8, 0.3]
                        }}
                        transition={{
                            duration: 3 + Math.random() * 2,
                            repeat: Infinity,
                            delay: Math.random() * 2
                        }}
                    />
                ))}

                {/* Workflow Steps in 3D Space */}
                {workflowSteps.map((step, index) => {
                    const isActive = index === activeStepIndex
                    const isCompleted = index < activeStepIndex
                    const isPending = index > activeStepIndex

                    return (
                        <motion.div
                            key={step.id}
                            className="absolute"
                            style={{
                                transform: `translate3d(${step.position.x}px, ${step.position.y}px, ${step.position.z}px)`,
                                transformStyle: 'preserve-3d'
                            }}
                            animate={{
                                scale: isActive ? [1, 1.2, 1] : 1,
                                rotateY: isActive ? [0, 360] : 0,
                            }}
                            transition={{
                                scale: { duration: 2, repeat: Infinity },
                                rotateY: { duration: 4, repeat: Infinity, ease: "linear" }
                            }}
                        >
                            {/* Step Node */}
                            <div className={`
                relative w-16 h-16 rounded-full flex items-center justify-center
                ${isActive ? `bg-gradient-to-r ${step.color} ${step.glowColor} shadow-2xl` : ''}
                ${isCompleted ? 'bg-gradient-to-r from-green-500 to-emerald-500 shadow-green-500/50 shadow-lg' : ''}
                ${isPending ? 'bg-gray-700 border-2 border-gray-500' : ''}
                transition-all duration-500
              `}>
                                <step.icon className={`
                  w-8 h-8 
                  ${isActive ? 'text-white animate-pulse' : ''}
                  ${isCompleted ? 'text-white' : ''}
                  ${isPending ? 'text-gray-400' : ''}
                `} />

                                {/* Active Step Glow Effect */}
                                {isActive && (
                                    <motion.div
                                        className={`absolute inset-0 rounded-full bg-gradient-to-r ${step.color} opacity-50`}
                                        animate={{
                                            scale: [1, 1.5, 1],
                                            opacity: [0.5, 0.8, 0.5]
                                        }}
                                        transition={{
                                            duration: 2,
                                            repeat: Infinity
                                        }}
                                    />
                                )}
                            </div>

                            {/* Step Label */}
                            <motion.div
                                className="absolute top-20 left-1/2 transform -translate-x-1/2 whitespace-nowrap"
                                style={{ transform: 'translateZ(20px)' }}
                                animate={{
                                    y: isActive ? [0, -5, 0] : 0
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity
                                }}
                            >
                                <div className={`
                  px-3 py-1 rounded-lg text-sm font-medium
                  ${isActive ? 'bg-white/20 text-white border border-white/30' : ''}
                  ${isCompleted ? 'bg-green-500/20 text-green-300 border border-green-500/30' : ''}
                  ${isPending ? 'bg-gray-700/50 text-gray-400 border border-gray-600' : ''}
                  backdrop-blur-sm
                `}>
                                    {step.name}
                                </div>
                            </motion.div>
                        </motion.div>
                    )
                })}

                {/* Connection Lines in 3D */}
                {workflowSteps.slice(0, -1).map((step, index) => {
                    const nextStep = workflowSteps[index + 1]
                    const isActive = index < activeStepIndex

                    return (
                        <motion.div
                            key={`line-${index}`}
                            className="absolute"
                            style={{
                                transform: `translate3d(${step.position.x + 32}px, ${step.position.y + 8}px, ${step.position.z}px)`,
                                transformStyle: 'preserve-3d'
                            }}
                        >
                            <div className={`
                h-0.5 bg-gradient-to-r
                ${isActive ? 'from-green-400 to-emerald-400 shadow-green-400/50 shadow-sm' : 'from-gray-600 to-gray-700'}
                transition-all duration-1000
              `}
                                style={{
                                    width: Math.sqrt(
                                        Math.pow(nextStep.position.x - step.position.x - 64, 2) +
                                        Math.pow(nextStep.position.y - step.position.y, 2)
                                    ),
                                    transform: `rotateZ(${Math.atan2(
                                        nextStep.position.y - step.position.y,
                                        nextStep.position.x - step.position.x - 64
                                    ) * 180 / Math.PI}deg)`
                                }} />
                        </motion.div>
                    )
                })}

                {/* Progress Orb */}
                <AnimatePresence>
                    {isRunning && (
                        <motion.div
                            className="absolute w-6 h-6 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full shadow-cyan-400/50 shadow-lg"
                            style={{
                                transformStyle: 'preserve-3d'
                            }}
                            animate={{
                                x: getCurrentStepPosition().x,
                                y: getCurrentStepPosition().y,
                                z: getCurrentStepPosition().z + 40,
                                rotateY: [0, 360]
                            }}
                            transition={{
                                x: { duration: 2, ease: "easeInOut" },
                                y: { duration: 2, ease: "easeInOut" },
                                z: { duration: 2, ease: "easeInOut" },
                                rotateY: { duration: 3, repeat: Infinity, ease: "linear" }
                            }}
                            initial={{ scale: 0 }}
                            exit={{ scale: 0 }}
                        />
                    )}
                </AnimatePresence>
            </div>

            {/* 3D Scene Controls */}
            <div className="absolute top-4 right-4 text-white/60 text-xs">
                <div>3D Workflow Visualization</div>
                <div>Step: {activeStepIndex + 1}/{workflowSteps.length}</div>
            </div>

            {/* Current Step Info */}
            <div className="absolute bottom-4 left-4 text-white">
                <div className="text-sm opacity-60">Current Step</div>
                <div className="text-lg font-semibold">
                    {workflowSteps[activeStepIndex]?.name || 'Ready'}
                </div>
            </div>
        </div>
    )
}