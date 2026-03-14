import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle, Circle, Loader } from 'lucide-react'

interface Step {
  id: string
  label: string
  status: 'pending' | 'active' | 'completed' | 'error'
}

interface LiveProgressProps {
  isRunning: boolean
  currentStep: string | null
  onStepChange: (step: string) => void
}

export default function LiveProgress({ isRunning, currentStep, onStepChange }: LiveProgressProps) {
  const [steps, setSteps] = useState<Step[]>([
    { id: 'detect', label: 'Detecting Changes', status: 'pending' },
    { id: 'analyze', label: 'Analyzing Diff', status: 'pending' },
    { id: 'generate', label: 'Generating Commit Message', status: 'pending' },
    { id: 'approve', label: 'Awaiting Approval', status: 'pending' },
    { id: 'commit', label: 'Committing Changes', status: 'pending' },
    { id: 'push_approve', label: 'Awaiting Push Approval', status: 'pending' },
    { id: 'push', label: 'Pushing to Remote', status: 'pending' },
  ])

  useEffect(() => {
    if (currentStep) {
      setSteps(prev => prev.map(step => {
        if (step.id === currentStep) {
          return { ...step, status: 'active' }
        }
        const currentIndex = prev.findIndex(s => s.id === currentStep)
        const stepIndex = prev.findIndex(s => s.id === step.id)
        if (stepIndex < currentIndex) {
          return { ...step, status: 'completed' }
        }
        return { ...step, status: 'pending' }
      }))
    }
  }, [currentStep])

  const getIcon = (status: Step['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-400" />
      case 'active':
        return <Loader className="w-5 h-5 text-blue-400 animate-spin" />
      case 'error':
        return <Circle className="w-5 h-5 text-red-400" />
      default:
        return <Circle className="w-5 h-5 text-gray-600" />
    }
  }

  return (
    <div className="space-y-4">
      <AnimatePresence>
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ delay: index * 0.1 }}
            className={`flex items-center gap-4 p-4 rounded-lg transition-all ${
              step.status === 'active'
                ? 'bg-blue-500/20 border border-blue-500/50'
                : step.status === 'completed'
                ? 'bg-green-500/10 border border-green-500/30'
                : 'bg-white/5 border border-white/10'
            }`}
          >
            <div className="flex-shrink-0">
              {getIcon(step.status)}
            </div>
            
            <div className="flex-1">
              <p className={`font-medium ${
                step.status === 'active' ? 'text-blue-400' :
                step.status === 'completed' ? 'text-green-400' :
                'text-gray-400'
              }`}>
                {step.label}
              </p>
            </div>

            {step.status === 'active' && (
              <motion.div
                className="flex-shrink-0"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ repeat: Infinity, duration: 1.5 }}
              >
                <div className="w-2 h-2 bg-blue-400 rounded-full" />
              </motion.div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>

      {!isRunning && (
        <div className="text-center text-gray-500 text-sm mt-6">
          Click "Run Agent" to start automation
        </div>
      )}
    </div>
  )
}
