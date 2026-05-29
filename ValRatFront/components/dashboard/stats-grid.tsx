import { Briefcase, TrendingUp, PiggyBank, Percent } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string
  subtitle?: string
  icon: React.ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  isLoading?: boolean
}

function StatCard({ title, value, subtitle, icon, trend, isLoading }: StatCardProps) {
  if (isLoading) {
    return (
      <Card className="border-border/50 shadow-sm">
        <CardContent className="p-5">
          <Skeleton className="h-4 w-24 mb-2" />
          <Skeleton className="h-8 w-32" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-all duration-300 group">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">{title}</p>
            <p className="text-2xl font-bold text-foreground tracking-tight">{value}</p>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            )}
            {trend && (
              <div className={cn(
                'inline-flex items-center gap-1 mt-2 text-xs font-medium px-2 py-0.5 rounded-full',
                trend.isPositive 
                  ? 'bg-emerald-50 text-emerald-700' 
                  : 'bg-red-50 text-red-700'
              )}>
                {trend.isPositive ? '+' : ''}{trend.value.toFixed(2)}%
              </div>
            )}
          </div>
          <div className="w-10 h-10 rounded-xl bg-accent flex items-center justify-center group-hover:bg-primary/10 transition-colors">
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

interface StatsGridProps {
  totalBalance: number
  totalInvested: number
  profitLoss: number
  percentChange: number
  isLoading?: boolean
}

export function StatsGrid({ 
  totalBalance, 
  totalInvested, 
  profitLoss, 
  percentChange,
  isLoading 
}: StatsGridProps) {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value)
  }

  const formatCurrencyFull = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Patrimônio"
        value={formatCurrency(totalBalance)}
        subtitle={formatCurrencyFull(totalBalance)}
        icon={<Briefcase className="h-5 w-5 text-primary" />}
        isLoading={isLoading}
      />
      <StatCard
        title="Total Investido"
        value={formatCurrency(totalInvested)}
        subtitle={formatCurrencyFull(totalInvested)}
        icon={<PiggyBank className="h-5 w-5 text-primary" />}
        isLoading={isLoading}
      />
      <StatCard
        title="Lucro/Prejuízo"
        value={formatCurrency(Math.abs(profitLoss))}
        icon={<TrendingUp className="h-5 w-5 text-primary" />}
        trend={{ value: percentChange, isPositive: profitLoss >= 0 }}
        isLoading={isLoading}
      />
      <StatCard
        title="Rentabilidade"
        value={`${percentChange >= 0 ? '+' : ''}${percentChange.toFixed(2)}%`}
        subtitle="Desde o início"
        icon={<Percent className="h-5 w-5 text-primary" />}
        isLoading={isLoading}
      />
    </div>
  )
}
