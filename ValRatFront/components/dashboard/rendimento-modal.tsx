"use client"

import { useState } from "react"
import { Calculator, TrendingUp, TrendingDown, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
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
    
    // Rendimento anualizado (CAGR)
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
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-foreground">
            <Calculator className="h-5 w-5 text-primary" />
            Calcular Rendimento
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Inputs */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="valorInicial">Valor Inicial (R$)</Label>
              <Input
                id="valorInicial"
                type="number"
                step="0.01"
                min="0"
                placeholder="10.000,00"
                value={valorInicial}
                onChange={(e) => setValorInicial(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="valorFinal">Valor Final (R$)</Label>
              <Input
                id="valorFinal"
                type="number"
                step="0.01"
                min="0"
                placeholder="12.500,00"
                value={valorFinal}
                onChange={(e) => setValorFinal(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="dataInicio">Data Início (opcional)</Label>
              <Input
                id="dataInicio"
                type="date"
                value={dataInicio}
                onChange={(e) => setDataInicio(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="dataFim">Data Fim (opcional)</Label>
              <Input
                id="dataFim"
                type="date"
                value={dataFim}
                onChange={(e) => setDataFim(e.target.value)}
              />
            </div>
          </div>

          {/* Botoes */}
          <div className="flex gap-2">
            <Button
              onClick={calcularRendimento}
              className="flex-1 bg-primary text-primary-foreground hover:bg-primary/90"
              disabled={!valorInicial || !valorFinal}
            >
              Calcular
            </Button>
            <Button
              variant="outline"
              onClick={limpar}
              className="border-primary/30 text-primary hover:bg-primary/5"
            >
              Limpar
            </Button>
          </div>

          {/* Resultado */}
          {resultado && (
            <div className="mt-4 rounded-xl border border-border bg-muted/30 p-4 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Rendimento</span>
                <div className="flex items-center gap-1">
                  {isPositivo ? (
                    <TrendingUp className="h-4 w-4 text-emerald-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span
                    className={`text-lg font-semibold ${
                      isPositivo ? "text-emerald-500" : "text-red-500"
                    }`}
                  >
                    {isPositivo ? "+" : ""}
                    {resultado.rendimentoPercentual.toFixed(2)}%
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Lucro/Prejuízo</span>
                <span
                  className={`font-medium ${
                    isPositivo ? "text-emerald-500" : "text-red-500"
                  }`}
                >
                  {isPositivo ? "+" : ""}
                  {formatarMoeda(resultado.rendimentoBruto)}
                </span>
              </div>

              {resultado.diasInvestido > 0 && (
                <>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Período</span>
                    <span className="font-medium text-foreground">
                      {resultado.diasInvestido} dias
                    </span>
                  </div>

                  <div className="flex items-center justify-between border-t border-border pt-3">
                    <span className="text-sm text-muted-foreground">
                      Rendimento Anualizado
                    </span>
                    <span
                      className={`font-semibold ${
                        resultado.rendimentoAnualizado >= 0
                          ? "text-emerald-500"
                          : "text-red-500"
                      }`}
                    >
                      {resultado.rendimentoAnualizado >= 0 ? "+" : ""}
                      {resultado.rendimentoAnualizado.toFixed(2)}% a.a.
                    </span>
                  </div>
                </>
              )}

              <div className="flex items-center justify-between text-xs text-muted-foreground pt-2 border-t border-border">
                <span>{formatarMoeda(resultado.valorInicial)}</span>
                <span>→</span>
                <span>{formatarMoeda(resultado.valorFinal)}</span>
              </div>
            </div>
          )}
        </div>

        <Button
          variant="ghost"
          size="icon"
          className="absolute right-4 top-4"
          onClick={handleClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </DialogContent>
    </Dialog>
  )
}
