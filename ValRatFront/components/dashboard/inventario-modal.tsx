"use client"

import { Boxes, RefreshCw, TrendingUp, TrendingDown, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { useInventario, type AtivoInventario } from "@/hooks/use-inventario"

interface InventarioModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const formatarMoeda = (valor: number) =>
  valor.toLocaleString("pt-BR", { style: "currency", currency: "BRL" })

const formatarQuantidade = (valor: number) => {
  // Cripto costuma ter casas decimais relevantes; ações/FIIs geralmente são inteiros.
  const temFracao = valor % 1 !== 0
  return valor.toLocaleString("pt-BR", {
    minimumFractionDigits: temFracao ? 2 : 0,
    maximumFractionDigits: 8,
  })
}

const rotuloTipo: Record<string, string> = {
  variavel: "Ação",
  acao: "Ação",
  fii: "FII",
  cripto: "Cripto",
  fixa: "Renda Fixa",
  "Renda Fixa": "Renda Fixa",
}

function LinhaAtivo({ ativo }: { ativo: AtivoInventario }) {
  const isPositivo = ativo.lucro >= 0

  return (
    <div className="flex items-center justify-between gap-3 rounded-lg border border-border/40 bg-secondary/30 px-3 py-2.5">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <span className="text-sm font-bold text-foreground font-mono tracking-tight">
            {ativo.ticker}
          </span>
          <span className="rounded-full bg-accent px-1.5 py-0.5 text-[10px] font-semibold text-accent-foreground">
            {rotuloTipo[ativo.tipo] ?? ativo.tipo}
          </span>
        </div>
        {ativo.nome && ativo.nome !== ativo.ticker && (
          <p className="truncate text-[11px] text-muted-foreground">{ativo.nome}</p>
        )}
        <p className="mt-0.5 text-[11px] text-muted-foreground font-mono">
          {formatarQuantidade(ativo.quantidade)} {ativo.quantidade === 1 ? "un" : "un"} · {formatarMoeda(ativo.preco)}
        </p>
      </div>

      <div className="flex flex-col items-end shrink-0">
        <span className="text-sm font-bold text-foreground font-mono">
          {formatarMoeda(ativo.valorTotal)}
        </span>
        <div className="flex items-center gap-0.5">
          {isPositivo ? (
            <TrendingUp className="h-3 w-3 text-success" />
          ) : (
            <TrendingDown className="h-3 w-3 text-destructive" />
          )}
          <span
            className={cn(
              "text-[11px] font-semibold font-mono",
              isPositivo ? "text-success" : "text-destructive"
            )}
          >
            {isPositivo ? "+" : ""}
            {ativo.variacao.toFixed(2)}%
          </span>
        </div>
      </div>
    </div>
  )
}

export function InventarioModal({ open, onOpenChange }: InventarioModalProps) {
  const {
    ativos,
    totalBalance,
    profitLoss,
    percentChange,
    isLoading,
    error,
    refetch,
  } = useInventario(open)

  const isPositivoTotal = profitLoss >= 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg border-border/60 bg-card p-6 relative overflow-hidden before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:bg-gradient-to-r before:from-transparent before:via-primary/40 before:to-transparent">
        <DialogHeader className="space-y-1">
          <div className="flex items-center justify-between gap-2 pr-6">
            <DialogTitle className="flex items-center gap-2 text-foreground font-bold tracking-tight">
              <Boxes className="h-4 w-4 text-primary" />
              Inventário de Ativos
            </DialogTitle>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 rounded-md text-muted-foreground hover:bg-muted disabled:opacity-50"
              onClick={refetch}
              disabled={isLoading}
              aria-label="Atualizar inventário"
            >
              <RefreshCw className={cn("h-3.5 w-3.5", isLoading && "animate-spin")} />
            </Button>
          </div>
          <DialogDescription className="text-xs text-muted-foreground">
            Posição atual de todos os ativos da sua carteira.
          </DialogDescription>
        </DialogHeader>

        {/* Resumo total */}
        <div className="rounded-lg border border-primary/10 bg-primary/[0.03] p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-muted-foreground">Patrimônio Total</span>
            <span className="text-base font-bold text-foreground font-mono tracking-tight">
              {formatarMoeda(totalBalance)}
            </span>
          </div>
          <div className="flex items-center justify-between border-t border-border/40 pt-2">
            <span className="text-xs font-medium text-muted-foreground">Resultado</span>
            <div className="flex items-center gap-1">
              {isPositivoTotal ? (
                <TrendingUp className="h-3 w-3 text-success" />
              ) : (
                <TrendingDown className="h-3 w-3 text-destructive" />
              )}
              <span
                className={cn(
                  "text-xs font-bold font-mono",
                  isPositivoTotal ? "text-success" : "text-destructive"
                )}
              >
                {isPositivoTotal ? "+" : ""}
                {formatarMoeda(profitLoss)} ({isPositivoTotal ? "+" : ""}
                {percentChange.toFixed(2)}%)
              </span>
            </div>
          </div>
        </div>

        {/* Lista de ativos */}
        <div className="mt-1 max-h-[360px] space-y-2 overflow-y-auto pr-1">
          {isLoading && ativos.length === 0 && (
            <div className="space-y-2">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="h-[58px] animate-pulse rounded-lg border border-border/40 bg-secondary/30"
                />
              ))}
            </div>
          )}

          {!isLoading && error && (
            <div className="flex items-center gap-2 rounded-lg border border-destructive/20 bg-destructive/5 px-3 py-2.5 text-xs text-destructive">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              {error}
            </div>
          )}

          {!isLoading && !error && ativos.length === 0 && (
            <div className="rounded-lg border border-border/40 bg-secondary/30 px-3 py-6 text-center text-xs text-muted-foreground">
              Nenhum ativo encontrado na sua carteira ainda.
            </div>
          )}

          {!error &&
            ativos.map((ativo, i) => (
              <LinhaAtivo key={`${ativo.ticker}-${i}`} ativo={ativo} />
            ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}