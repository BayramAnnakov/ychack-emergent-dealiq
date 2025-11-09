import React from 'react'

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Executive Summary Skeleton */}
      <div className="mb-6">
        <div className="mb-4">
          <div className="h-8 w-64 bg-gray-200 rounded animate-pulse mb-2"></div>
          <div className="h-4 w-48 bg-gray-100 rounded animate-pulse"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="bg-white rounded-xl p-5 border border-gray-200 animate-pulse"
              style={{ animationDelay: `${i * 100}ms` }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="h-12 w-12 bg-gray-200 rounded-xl"></div>
                <div className="h-5 w-12 bg-gray-100 rounded-full"></div>
              </div>
              <div>
                <div className="h-4 w-24 bg-gray-100 rounded mb-2"></div>
                <div className="h-10 w-32 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tabs Skeleton */}
      <div className="card">
        <div className="border-b border-gray-200 mb-6">
          <div className="flex space-x-4">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="h-10 w-32 bg-gray-100 rounded-t animate-pulse"
              ></div>
            ))}
          </div>
        </div>

        {/* Quick Insights Skeleton */}
        <div className="space-y-6">
          <div>
            <div className="h-6 w-40 bg-gray-200 rounded mb-4 animate-pulse"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[1, 2, 3, 4].map((i) => (
                <div
                  key={i}
                  className="bg-gradient-to-br from-gray-50 to-white rounded-xl p-4 border border-gray-200 animate-pulse"
                  style={{ animationDelay: `${i * 100}ms` }}
                >
                  <div className="flex items-start gap-3">
                    <div className="h-10 w-10 bg-gray-200 rounded-lg"></div>
                    <div className="flex-1">
                      <div className="h-5 w-3/4 bg-gray-200 rounded mb-2"></div>
                      <div className="h-4 w-full bg-gray-100 rounded mb-1"></div>
                      <div className="h-4 w-5/6 bg-gray-100 rounded"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Charts Skeleton */}
          <div className="space-y-6">
            <div className="card">
              <div className="h-6 w-48 bg-gray-200 rounded mb-4 animate-pulse"></div>
              <div className="h-64 bg-gray-100 rounded-lg animate-pulse"></div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {[1, 2].map((i) => (
                <div key={i} className="card">
                  <div className="h-6 w-40 bg-gray-200 rounded mb-4 animate-pulse"></div>
                  <div className="h-56 bg-gray-100 rounded-lg animate-pulse"></div>
                </div>
              ))}
            </div>

            <div className="card">
              <div className="h-6 w-40 bg-gray-200 rounded mb-4 animate-pulse"></div>
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center gap-4 animate-pulse">
                    <div className="h-6 w-1/4 bg-gray-100 rounded"></div>
                    <div className="h-6 w-1/6 bg-gray-100 rounded"></div>
                    <div className="h-6 w-1/6 bg-gray-100 rounded"></div>
                    <div className="h-6 flex-1 bg-gray-100 rounded"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSkeleton
