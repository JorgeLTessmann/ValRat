'use client'

import { Briefcase, Plus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

interface EmptyStateProps {
  onAddInvestment?: () => void
}

export function EmptyState({ onAddInvestment }: EmptyStateProps) {
  return (
    <Card className="border-border/50 shadow-sm">
      <CardContent className="flex flex-col items-center justify-center py-16 px-8 text-center">
        <div className="w-16 h-16 rounded-full bg-accent flex items-center justify-center mb-6">
          <Briefcase className="h-8 w-8 text-primary" />
        </div>
        
        <h3 className="text-xl font-semibold text-foreground mb-2">
          Nenhum investimento ainda
        </h3>
        
        <p className="text-muted-foreground max-w-sm mb-6">
          Comece a construir seu portfólio adicionando seu primeiro investimento. 
          Acompanhe suas ações, ETFs, FIIs, criptos e renda fixa em um só lugar.
        </p>
        
        <Button 
          onClick={onAddInvestment}
          className="bg-primary hover:bg-primary/90 text-primary-foreground"
        >
          <Plus className="h-4 w-4 mr-2" />
          Adicionar Primeiro Investimento
        </Button>
      </CardContent>
    </Card>
  )
}
