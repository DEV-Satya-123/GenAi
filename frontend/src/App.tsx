import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'
import WorkflowGraph3D from './components/WorkflowGraph3D'
import LiveProgress from './components/LiveProgress'
import Header from './components/Header'
import StatusCard from './components/StatusCard'

function App() {
  const [isRunning, setIsRunning] = useState(false)
  const [currentStep, setCurrentStep] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <h1 className="text-5xl font-bold text-center mb-4 gradient-text">
            AI Git Automation
          </h1>
          <p className="text-center text-gray-400 mb-12">
            Intelligent commit message generation powered by Google Gemini
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <StatusCard />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass rounded-2xl p-6 h-[500px]"
          >
            <h2 className="text-2xl font-bold mb-4">Workflow Visualization</h2>
            <WorkflowGraph3D currentStep={currentStep} />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-2xl p-6"
          >
            <h2 className="text-2xl font-bold mb-4">Live Progress</h2>
            <LiveProgress 
              isRunning={isRunning}
              currentStep={currentStep}
              onStepChange={setCurrentStep}
            />
          </motion.div>
        </div>

        <Dashboard 
          onRunStart={() => setIsRunning(true)}
          onRunEnd={() => setIsRunning(false)}
        />
      </main>
    </div>
  )
}

export default App
