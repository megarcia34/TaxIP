import ClientLayout from './ClientLayout'

export const dynamic = 'force-dynamic'

export default function PropietarioLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <ClientLayout>{children}</ClientLayout>
}