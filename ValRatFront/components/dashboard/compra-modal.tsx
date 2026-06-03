'use client'

import { useState } from 'react'
import { Plus, Info } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

function hojeISO() {
  return new Date().toISOString().slice(0, 10)
}

export function CompraModal({ open, onClose, onSuccess }: Props) {
  const [categoria, setCategoria] = useState('variavel')
  const [ticker, setTicker] = useState('')
  const [quantidade, setQuantidade] = useState(1)
  const [valorAplicado, setValorAplicado] = useState('')
  const [dataCompra, setDataCompra] = useState(hojeISO())
  const [plataforma, setPlataforma] = useState('xp')
  const [taxa, setTaxa] = useState('')
  const [indexador, setIndexador] = useState('CDI')
  const [tipoRendaFixa, setTipoRendaFixa] = useState('cdb') // NOVO: 'cdb', 'lci', 'lca', 'tesouro'
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')

  const isRendaFixa = categoria === 'fixa'
  const isCripto = categoria === 'cripto'

  const salvar = async () => {
    setErro('')
    setSalvando(true)

    try {
      const body: any = {
        categoria,
        ticker: ticker.trim().toUpperCase(),
        data_compra: dataCompra,
        plataforma,
      }

      if (isRendaFixa) {
        body.valor_investido = Number(valorAplicado)
        body.quantidade = 1
        body.taxa = Number(taxa)
        body.indexador = indexador
        body.tipo_renda_fixa = tipoRendaFixa  // NOVO
      } else {
        body.quantidade = Number(quantidade)
      }

      const response = await fetch('http://127.0.0.1:8000/compras', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })

      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.erro || result.detail || 'Erro ao cadastrar')
      }

      // Limpa o formulário
      setTicker('')
      setQuantidade(1)
      setValorAplicado('')
      setDataCompra(hojeISO())
      setPlataforma('xp')
      setCategoria('variavel')
      setTaxa('')
      setIndexador('CDI')
      setTipoRendaFixa('cdb')

      onSuccess()
      onClose()

    } catch (err: any) {
      setErro(err.message)
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => { if (!isOpen) onClose() }}>
      <DialogContent className="border-border/50 sm:max-w-md gap-5">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-accent-foreground">
            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-accent">
              <Plus className="h-4 w-4 text-primary" />
            </span>
            Novo aporte
          </DialogTitle>
          <DialogDescription>
            Cadastre um novo ativo na sua carteira.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4">
          {/* Categoria */}
          <div className="grid gap-2">
            <Label htmlFor="categoria">Categoria do ativo</Label>
            <Select value={categoria} onValueChange={setCategoria}>
              <SelectTrigger id="categoria" className="w-full">
                <SelectValue placeholder="Selecione a categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="variavel">📈 Renda Variável (Ações, ETFs, FIIs)</SelectItem>
                <SelectItem value="fixa">📉 Renda Fixa (CDB, LCI, LCA, Tesouro)</SelectItem>
                <SelectItem value="cripto">₿ Criptomoedas (BTC, ETH, etc)</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              A categoria é apenas para organização visual dos seus investimentos.
            </p>
          </div>

          {/* Ticker / Código */}
          <div className="grid gap-2">
            <Label htmlFor="ticker">
              {isCripto ? 'Código da criptomoeda' : 'Ticker / Código'}
            </Label>
            <Input
              id="ticker"
              placeholder={isCripto ? 'Ex: BTC, ETH, SOL' : 'Ex: CDB_INTER_110, PETR4'}
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
            />
          </div>

          {/* Quantidade ou Valor aplicado */}
          {isRendaFixa ? (
            <div className="grid gap-2">
              <Label htmlFor="valor">Valor aplicado (R$)</Label>
              <Input
                id="valor"
                type="number"
                step="any"
                placeholder="Ex: 1000"
                value={valorAplicado}
                onChange={(e) => setValorAplicado(e.target.value)}
              />
            </div>
          ) : (
            <div className="grid gap-2">
              <Label htmlFor="quantidade">Quantidade</Label>
              <Input
                id="quantidade"
                type="number"
                step="any"
                placeholder="Ex: 10"
                value={quantidade}
                onChange={(e) => setQuantidade(Number(e.target.value))}
              />
            </div>
          )}

          {/* Campos adicionais para Renda Fixa */}
          {isRendaFixa && (
            <>
              <div className="grid gap-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="tipoRendaFixa">Tipo do ativo</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>LCI e LCA são isentos de Imposto de Renda.</p>
                        <p>Tesouro Direto tem tributação regressiva.</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Select value={tipoRendaFixa} onValueChange={setTipoRendaFixa}>
                  <SelectTrigger id="tipoRendaFixa" className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="cdb">CDB</SelectItem>
                    <SelectItem value="lci">LCI (Isento IR)</SelectItem>
                    <SelectItem value="lca">LCA (Isento IR)</SelectItem>
                    <SelectItem value="tesouro">Tesouro Direto</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="taxa">Taxa (%)</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent className="max-w-xs">
                        <p>Informe a taxa contratual (ex: 110 para 110% do CDI).</p>
                        <p className="text-xs mt-1">Para Tesouro Prefixado, informe a taxa anual.</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Input
                  id="taxa"
                  type="number"
                  step="any"
                  placeholder="Ex: 100, 110, 12.5"
                  value={taxa}
                  onChange={(e) => setTaxa(e.target.value)}
                />
              </div>

              <div className="grid gap-2">
                <div className="flex items-center gap-2">
                  <Label htmlFor="indexador">Indexador</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>Indexador que rege a rentabilidade do ativo.</p>
                        <p>CDI = pós-fixado, IPCA = inflação, PRE = prefixado.</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Select value={indexador} onValueChange={setIndexador}>
                  <SelectTrigger id="indexador" className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CDI">CDI (pós-fixado)</SelectItem>
                    <SelectItem value="IPCA">IPCA (inflação)</SelectItem>
                    <SelectItem value="PRE">Prefixado (taxa fixa)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </>
          )}

          {/* Data */}
          <div className="grid gap-2">
            <Label htmlFor="data">Data da aplicação</Label>
            <Input
              id="data"
              type="date"
              value={dataCompra}
              onChange={(e) => setDataCompra(e.target.value)}
            />
          </div>

          {/* Plataforma */}
          <div className="grid gap-2">
            <Label htmlFor="plataforma">Plataforma</Label>
            <Select value={plataforma} onValueChange={setPlataforma}>
              <SelectTrigger id="plataforma" className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="xp">XP Investimentos</SelectItem>
                <SelectItem value="inter">Banco Inter</SelectItem>
                <SelectItem value="itau">Itaú</SelectItem>
                <SelectItem value="nubank">Nubank</SelectItem>
                <SelectItem value="clear">Clear</SelectItem>
                <SelectItem value="rico">Rico</SelectItem>
                <SelectItem value="btg">BTG Pactual</SelectItem>
                <SelectItem value="outro">Outro</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Erro */}
          {erro && (
            <p className="text-sm text-destructive">
              {erro}
            </p>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-2">
          <Button type="button" variant="outline" onClick={onClose} disabled={salvando}>
            Cancelar
          </Button>
          <Button type="button" onClick={salvar} disabled={salvando}>
            {salvando ? 'Salvando...' : 'Salvar'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}