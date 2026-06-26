'use client'

import {
  Plus,
  Tag,
  type LucideIcon
} from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface QuickAction {
  id: string
  label: string
  icon: LucideIcon
  isPrimary?: boolean
}

interface QuickActionsProps {
  onComprarClick: () => void
  onVenderClick: () => void
}

const quickActions: QuickAction[] = [
  {
    id: 'deposit',
    label: 'Novo Aporte',
    icon: Plus,
    isPrimary: true
  },
  {
    id: 'sell',
    label: 'Vender Ativo',
    icon: Tag
  }
]

export function QuickActions({
  onComprarClick,
  onVenderClick
}: QuickActionsProps) {

  const handleAction = (actionId: string) => {

    if (actionId === 'buy' || actionId === 'deposit') {
      onComprarClick()
    }

    if (actionId === 'sell') {
      onVenderClick()
    }
  }

  return (
    <Card className="border-border/50 shadow-sm hover:shadow-md transition-shadow duration-300">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg font-semibold text-accent-foreground">
          Ações Rápidas
        </CardTitle>
      </CardHeader>

      <CardContent>
        <div className="grid grid-cols-2 gap-3">

          {quickActions.map((action) => (

            <Button
              key={action.id}
              variant={action.isPrimary ? 'default' : 'outline'}
              className={cn(
                'h-auto py-4 px-4 flex flex-col items-center gap-2 transition-all duration-200',

                action.isPrimary
                  ? 'bg-primary hover:bg-primary/90 text-primary-foreground shadow-sm hover:shadow-md'
                  : 'border-primary/30 text-accent-foreground hover:bg-accent hover:border-primary/50'
              )}

              onClick={() => handleAction(action.id)}
            >

              <action.icon
                className={cn(
                  'h-5 w-5',
                  action.isPrimary
                    ? 'text-primary-foreground'
                    : 'text-primary'
                )}
              />

              <span className="text-xs font-medium text-center leading-tight">
                {action.label}
              </span>

            </Button>

          ))}

        </div>
      </CardContent>
    </Card>
  )
}