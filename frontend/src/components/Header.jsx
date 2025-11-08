import React from 'react'
import { Brain, TrendingUp } from 'lucide-react'

function Header() {
  return (
    <header className="bg-white border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-primary-600 p-2 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">DealIQ</h1>
              <p className="text-sm text-gray-600">Every Rep's Personal Data Scientist</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <TrendingUp className="h-4 w-4" />
              <span>AI-Powered CRM Intelligence</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header