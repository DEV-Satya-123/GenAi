import { GitBranch, Sparkles } from 'lucide-react'
import { motion } from 'framer-motion'

export default function Header() {
    return (
        <motion.header
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            className="glass border-b border-white/10"
        >
            <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                        <GitBranch className="w-6 h-6" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold">AI Git Automation</h1>
                        <p className="text-xs text-gray-400">Powered by Gemini AI</p>
                    </div>
                </div>

                <div className="flex items-center gap-2 px-4 py-2 glass rounded-full">
                    <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
                    <span className="text-sm">Live</span>
                </div>
            </div>
        </motion.header>
    )
}
