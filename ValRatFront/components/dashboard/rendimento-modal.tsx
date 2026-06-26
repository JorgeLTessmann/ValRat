"use client"

import { useState } from "react"
import { Calculator, TrendingUp, TrendingDown, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"

interface RendimentoModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

interface ResultadoRendimento {
  valorInicial: number
  valorFinal: number
  rendimentoBruto: number
  rendimentoPercentual: number
  diasInvestido: number
  rendimentoAnualizado: number
}

export function RendimentoModal({ open, onOpenChange }: RendimentoModalProps) {
  const [valorInicial, setValorInicial] = useState("")
  const [valorFinal, setValorFinal] = useState("")
  const [dataInicio, setDataInicio] = useState("")
  const [dataFim, setDataFim] = useState("")
  const [resultado, setResultado] = useState<ResultadoRendimento | null>(null)

  const calcularRendimento = () => {
    const inicial = parseFloat(valorInicial)
    const final = parseFloat(valorFinal)
    
    if (isNaN(inicial) || isNaN(final) || inicial <= 0) {
      return
    }

    const inicio = dataInicio ? new Date(dataInicio) : null
    const fim = dataFim ? new Date(dataFim) : new Date()
    
    const diasInvestido = inicio && fim 
      ? Math.ceil((fim.getTime() - inicio.getTime()) / (1000 * 60 * 60 * 24))
      : 0

    const rendimentoBruto = final - inicial
    const rendimentoPercentual = ((final - inicial) / inicial) * 100
    
    const anos = diasInvestido / 365
    const rendimentoAnualizado = anos > 0 
      ? (Math.pow(final / inicial, 1 / anos) - 1) * 100
      : rendimentoPercentual

    setResultado({
      valorInicial: inicial,
      valorFinal: final,
      rendimentoBruto,
      rendimentoPercentual,
      diasInvestido,
      rendimentoAnualizado,
    })
  }

  const limpar = () => {
    setValorInicial("")
    setValorFinal("")
    setDataInicio("")
    setDataFim("")
    setResultado(null)
  }

  const handleClose = () => {
    limpar()
    onOpenChange(false)
  }

  const formatarMoeda = (valor: number) => {
    return valor.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    })
  }

  const isPositivo = resultado ? resultado.rendimentoBruto >= 0 : true

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md border-border/60 bg-card p-6 relative overflow-hidden before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-[#D4AF37]/40 before:to-transparent">
        <DialogHeader className="space-y-1">
          <DialogTitle className="flex items-center gap-2 text-foreground font-bold tracking-tight">
            <Calculator className="h-4 w-4 text-[#D4AF37]" />
            Calcular Rendimento
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Insira os valores para analisar a performance do seu aporte.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-3">
          {/* Inputs de Valores Numéricos - Fonte Mono */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="valorInicial" className="text-xs text-muted-foreground font-medium">Valor Inicial</Label>
              <div className="relative">
                <span className="absolute left-2.5 top-2 text-xs font-semibold text-muted-foreground/60">R$</span>
                <Input
                  id="valorInicial"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0,00"
                  className="pl-8 h-8 text-sm font-mono focus-visible:ring-[#D4AF37]/30"
                  value={valorInicial}
                  onChange={(e) => setValorInicial(e.target.value)}
                />
              </div>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="valorFinal" className="text-xs text-muted-foreground font-medium">Valor Final</Label>
              <div className="relative">
                <span className="absolute left-2.5 top-2 text-xs font-semibold text-muted-foreground/60">R$</span>
                <Input
                  id="valorFinal"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="0,00"
                  className="pl-8 h-8 text-sm font-mono focus-visible:ring-[#D4AF37]/30"
                  value={valorFinal}
                  onChange={(e) => setValorFinal(e.target.value)}
                />
              </div>
            </div>
          </div>

          {/* Inputs de Datas - Formato padrão do sistema */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="dataInicio" className="text-xs text-muted-foreground font-medium">Data Início</Label>
              <Input
                id="dataInicio"
                type="date"
                className="h-8 text-xs focus-visible:ring-[#D4AF37]/30"
                value={dataInicio}
                onChange={(e) => setDataInicio(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="dataFim" className="text-xs text-muted-foreground font-medium">Data Fim</Label>
              <Input
                id="dataFim"
                type="date"
                className="h-8 text-xs focus-visible:ring-[#D4AF37]/30"
                value={dataFim}
                onChange={(e) => setDataFim(e.target.value)}
              />
            </div>
          </div>

          {/* Botões de Ação */}
          <div className="flex gap-2 pt-2">
            <Button
              onClick={calcularRendimento}
              className="flex-1 h-8 text-xs font-bold bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-background transition-colors"
              disabled={!valorInicial || !valorFinal}
            >
              Calcular
            </Button>
            <Button
              variant="outline"
              onClick={limpar}
              className="h-8 text-xs border-border text-muted-foreground hover:bg-muted"
            >
              Limpar
            </Button>
          </div>

          {/* Resultados Internos com Regra de Fontes Estrita */}
          {resultado && (
            <div className="mt-2 rounded-lg border border-amber-500/10 bg-amber-500/[0.01] p-3 space-y-2.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">Rendimento Percentual</span>
                <div className="flex items-center gap-1">
                  {isPositivo ? (
                    <TrendingUp className="h-3 w-3 text-emerald-500" />
                  ) : (
                    <TrendingDown className="h-3 w-3 text-rose-500" />
                  )}
                  <span className={cn(
                    "text-sm font-bold font-mono tracking-tight",
                    isPositivo ? "text-emerald-500" : "text-rose-500"
                  )}>
                    {isPositivo ? "+" : ""}{resultado.rendimentoPercentual.toFixed(2)}%
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-muted-foreground">Lucro/Prejuízo</span>
                <span className={cn(
                  "text-xs font-bold font-mono",
                  isPositivo ? "text-emerald-500" : "text-rose-500"
                )}>
                  {isPositivo ? "+" : ""}{formatarMoeda(resultado.rendimentoBruto)}
                </span>
              </div>

              {resultado.diasInvestido > 0 && (
                <>
                  <div className="flex items-center justify-between border-t border-border/40 pt-2">
                    <span className="text-xs font-medium text-muted-foreground">Período</span>
                    <span className="text-xs font-bold text-foreground font-mono">
                      {resultado.diasInvestido} <span className="text-[10px] font-medium text-muted-foreground font-sans">dias</span>
                    </span>
                  </div>

                  <div className="flex items-center justify-between border-t border-border/40 pt-2">
                    <span className="text-xs font-medium text-muted-foreground font-sans">Rendimento Anualizado</span>
                    <span className={cn(
                      "text-xs font-bold font-mono",
                      resultado.rendimentoAnualizado >= 0 ? "text-[#D4AF37]" : "text-rose-500"
                    )}>
                      {resultado.rendimentoAnualizado >= 0 ? "+" : ""}{resultado.rendimentoAnualizado.toFixed(2)}% <span className="text-[10px] font-medium text-muted-foreground font-sans">a.a.</span>
                    </span>
                  </div>
                </>
              )}

              <div className="flex items-center justify-between text-[10px] text-muted-foreground/60 pt-2 border-t border-border/40 font-mono">
                <span>{formatarMoeda(resultado.valorInicial)}</span>
                <span className="font-sans">→</span>
                <span className="text-foreground/80">{formatarMoeda(resultado.valorFinal)}</span>
              </div>
            </div>
          )}
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="absolute right-3 top-3 h-6 w-6 rounded-md text-muted-foreground hover:bg-muted"
          onClick={handleClose}
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </DialogContent>
    </Dialog>
  )
}