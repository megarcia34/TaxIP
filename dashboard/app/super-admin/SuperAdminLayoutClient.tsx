'use client'

import { ReactNode, useState } from 'react'
import SuperAdminSidebar from '@/components/super-admin/SuperAdminSidebar'
import { Header } from '@/components/layout/Header'

interface SuperAdminLayoutClientProps {
  children: ReactNode
}

export default function SuperAdminLayoutClient({ children }: SuperAdminLayoutClientProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <SuperAdminSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}