import { useState } from 'react'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'
import Header from './components/Header'
import StatusCard from './components/StatusCard'

function App() {
  const [isRunning, setIsRunning] = useState(false)

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

        <Dashboard 
          onRunStart={() => setIsRunning(true)}
          onRunEnd={() => setIsRunning(false)}
        />
      </main>
    </div>
  )
}

export default App
