'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { ChevronRight, TrendingUp, TrendingDown, Info } from 'lucide-react'
import { cn } from '@/lib/utils'

interface KPICardProps {
  title: string
  value: number
  trend?: number
  icon: React.ReactNode
  detailData?: Array<{ vehiculo_id: string; patente: string; valor: number; viajes?: number }>
  detailTitle?: string
  detailValueLabel?: string
  detailSecondaryLabel?: string
  className?: string
  loading?: boolean
}

export function KPICard({
  title,
  value,
  trend,
  icon,
  detailData,
  detailTitle = 'Desglose por vehículo',
  detailValueLabel = 'Monto',
  detailSecondaryLabel = 'Viajes',
  className,
  loading = false,
}: KPICardProps) {
  const trendColor =
    trend && trend > 0 ? 'text-green-500' : trend && trend < 0 ? 'text-red-500' : 'text-muted-foreground'
  const TrendIcon = trend && trend > 0 ? TrendingUp : trend && trend < 0 ? TrendingDown : null

  const hasDetail = detailData && detailData.length > 0

  return (
    <Card className={cn('transition-all hover:shadow-md', className)}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary">
          {icon}
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="h-8 w-24 animate-pulse rounded bg-muted" />
        ) : (
          <div className="text-2xl font-bold">${value.toLocaleString()}</div>
        )}
        {trend !== undefined && !loading && (
          <p className={cn('text-xs flex items-center gap-1 mt-1', trendColor)}>
            {TrendIcon && <TrendIcon className="h-3 w-3" />}
            {trend > 0 ? '+' : ''}
            {trend}% vs ayer
          </p>
        )}

        {hasDetail && !loading && (
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="sm" className="mt-3 p-0 h-auto text-xs text-muted-foreground hover:text-foreground">
                Ver desglose <ChevronRight className="h-3 w-3 ml-1" />
              </Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>{detailTitle}</SheetTitle>
              </SheetHeader>
              <div className="mt-6">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Vehículo</TableHead>
                      <TableHead className="text-right">{detailValueLabel}</TableHead>
                      {detailSecondaryLabel && <TableHead className="text-right">{detailSecondaryLabel}</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {detailData.map((item) => (
                      <TableRow key={item.vehiculo_id}>
                        <TableCell className="font-medium">{item.patente}</TableCell>
                        <TableCell className="text-right font-mono">${item.valor.toLocaleString()}</TableCell>
                        {detailSecondaryLabel && (
                          <TableCell className="text-right">{item.viajes ?? '-'}</TableCell>
                        )}
                      </TableRow>
                    ))}
                    <TableRow className="border-t-2">
                      <TableCell className="font-bold">Total</TableCell>
                      <TableCell className="text-right font-bold font-mono">
                        ${detailData.reduce((acc, d) => acc + d.valor, 0).toLocaleString()}
                      </TableCell>
                      {detailSecondaryLabel && (
                        <TableCell className="text-right font-bold">
                          {detailData.reduce((acc, d) => acc + (d.viajes ?? 0), 0)}
                        </TableCell>
                      )}
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </SheetContent>
          </Sheet>
        )}
      </CardContent>
    </Card>
  )
}