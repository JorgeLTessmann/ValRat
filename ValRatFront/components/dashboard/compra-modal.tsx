'use client'

import { useState } from 'react'
import { Plus, Info, Calendar, DollarSign, Tag, AlertCircle } from 'lucide-react'
import { useAuth } from '@/hooks/use-auth' // <-- IMPORT ATUALIZADO
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip'
import { Switch } from '@/components/ui/switch'

interface Props {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

function hojeISO() {
  return new Date().toISOString().slice(0, 10)
}

export function CompraModal({ open, onClose, onSuccess }: Props) {
  // <-- USANDO SEU HOOK NATIVO AQUI
  const { currentUser } = useAuth()

  // =========================
  // Estados comuns
  // =========================
  const [categoria, setCategoria] = useState<'variavel' | 'fixa' | 'cripto'>('variavel')
  const [plataforma, setPlataforma] = useState('xp')
  const [dataCompra, setDataCompra] = useState(hojeISO())
  const [salvando, setSalvando] = useState(false)
  const [erro, setErro] = useState('')

  // =========================
  // Estados específicos – Renda Variável / Cripto
  // =========================
  const [ticker, setTicker] = useState('')
  const [quantidade, setQuantidade] = useState(1)

  // =========================
  // Estados específicos – Renda Fixa
  // =========================
  const [nomeAplicacao, setNomeAplicacao] = useState('')
  const [valorAplicado, setValorAplicado] = useState('')
  const [dataVencimento, setDataVencimento] = useState('')
  const [temCarencia, setTemCarencia] = useState(false)
  const [dataCarencia, setDataCarencia] = useState('')
  const [tipoAtivo, setTipoAtivo] = useState<'cdb' | 'lci' | 'lca' | 'tesouro'>('cdb')
  const [indexador, setIndexador] = useState<'CDI' | 'IPCA' | 'PRE'>('CDI')
  const [taxaContratada, setTaxaContratada] = useState('')

  // =========================
  // Helpers
  // =========================
  const isRendaFixa = categoria === 'fixa'
  const isCripto = categoria === 'cripto'

  const getPlataformas = () => {
    if (categoria === 'variavel') return ['xp', 'clear', 'rico', 'itau', 'bradesco', 'outro']
    if (categoria === 'fixa') return ['inter', 'nubank', 'btg', 'xp', 'itau', 'outro']
    if (categoria === 'cripto') return ['binance', 'mercadobitcoin', 'coinbase', 'foxbit', 'outro']
    return ['xp', 'inter', 'nubank', 'outro']
  }

  const getTaxaLabel = () => {
    if (indexador === 'CDI') {
      return {
        label: 'Rentabilidade (% do CDI)',
        placeholder: 'Ex: 110',
        tip: 'Percentual do CDI contratado. Ex: 100 = 100% do CDI, 110 = 110% do CDI.',
      }
    }
    if (indexador === 'IPCA') {
      return {
        label: 'Taxa real acima do IPCA (% a.a.)',
        placeholder: 'Ex: 6.5',
        tip: 'Apenas o cupom fixo anual acima da inflação. Ex: IPCA + 6,5% → digitar 6.5',
      }
    }
    return {
      label: 'Taxa pré‑fixada (% a.a.)',
      placeholder: 'Ex: 12.75',
      tip: 'Taxa anual bruta fechada no momento da aplicação.',
    }
  }

  const getIsencaoTooltip = () => {
    if (tipoAtivo === 'lci' || tipoAtivo === 'lca') {
      return 'LCI e LCA são isentos de Imposto de Renda para pessoa física.'
    }
    if (tipoAtivo === 'tesouro') {
      return 'Tesouro Direto segue a tabela regressiva de IR (22,5% a 15% conforme o prazo).'
    }
    return 'CDB segue a tabela regressiva de IR (22,5% a 15% conforme o prazo).'
  }

  // =========================
  // Validação e envio
  // =========================
  const salvar = async () => {
    setErro('')
    setSalvando(true)

    const userEmail = currentUser?.email || (typeof currentUser === 'string' ? currentUser : null)

    if (!userEmail) {
      setErro('Usuário não identificado no sistema. Faça login novamente.')
      setSalvando(false)
      return
    }

    if (!dataCompra) {
      setErro('Data da aplicação é obrigatória')
      setSalvando(false)
      return
    }

    // ========== RENDA FIXA ==========
    if (isRendaFixa) {
      if (!nomeAplicacao.trim()) {
        setErro('Nome da aplicação é obrigatório')
        setSalvando(false)
        return
      }
      if (!valorAplicado || Number(valorAplicado) <= 0) {
        setErro('Valor aplicado deve ser maior que zero')
        setSalvando(false)
        return
      }
      if (!dataVencimento) {
        setErro('Data de vencimento é obrigatória')
        setSalvando(false)
        return
      }
      if (new Date(dataVencimento) <= new Date(dataCompra)) {
        setErro('Vencimento deve ser posterior à data de aplicação')
        setSalvando(false)
        return
      }
      if (temCarencia && !dataCarencia) {
        setErro('Data de carência é obrigatória quando há carência')
        setSalvando(false)
        return
      }
      if (temCarencia && new Date(dataCarencia) >= new Date(dataVencimento)) {
        setErro('Data de carência deve ser anterior ao vencimento')
        setSalvando(false)
        return
      }
      if (!taxaContratada || Number(taxaContratada) <= 0) {
        const helper = getTaxaLabel()
        setErro(`${helper.label} é obrigatória`)
        setSalvando(false)
        return
      }

      const body = {
        categoria: "Renda Fixa",
        data_compra: dataCompra,
        plataforma: plataforma || null,
        nome_aplicacao: nomeAplicacao.trim(),
        valor_investido: Number(valorAplicado),
        data_vencimento: dataVencimento,
        tipo_renda_fixa: tipoAtivo,
        indexador: indexador,
        taxa_contratada: Number(taxaContratada),
        tem_carencia: temCarencia,
        data_carencia: temCarencia ? dataCarencia : null,
      }

      try {
        const response = await fetch('https://valrat.onrender.com/renda-fixa', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-User-Email': userEmail
          },
          body: JSON.stringify(body),
        })
        const result = await response.json()
        if (!response.ok) throw new Error(result.erro || result.detail)

        setNomeAplicacao('')
        setValorAplicado('')
        setDataVencimento('')
        setTemCarencia(false)
        setDataCarencia('')
        setTipoAtivo('cdb')
        setIndexador('CDI')
        setTaxaContratada('')
        onSuccess()
        onClose()
      } catch (err: any) {
        setErro(err.message)
      } finally {
        setSalvando(false)
      }
      return
    }

    // ========== RENDA VARIÁVEL / CRIPTO ==========
    if (!ticker.trim()) {
      setErro(isCripto ? 'Código da criptomoeda é obrigatório' : 'Ticker é obrigatório')
      setSalvando(false)
      return
    }
    if (quantidade <= 0) {
      setErro('Quantidade deve ser maior que zero')
      setSalvando(false)
      return
    }

    const body = {
      categoria,
      ticker: ticker.trim().toUpperCase(),
      data_compra: dataCompra,
      plataforma,
      quantidade: Number(quantidade),
    }

    try {
      const response = await fetch('https://valrat.onrender.com/compras', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Email': userEmail
        },
        body: JSON.stringify(body),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.erro || result.detail)

      setTicker('')
      setQuantidade(1)
      onSuccess()
      onClose()
    } catch (err: any) {
      setErro(err.message)
    } finally {
      setSalvando(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && onClose()}>
      <DialogContent className="sm:max-w-[550px] gap-6 p-6 overflow-y-auto max-h-[90vh]">
        <DialogHeader className="space-y-1.5">
          <DialogTitle className="text-xl font-semibold tracking-tight text-foreground flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-border bg-muted/50 text-muted-foreground">
              <Plus className="h-4 w-4" />
            </div>
            Novo aporte
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            Cadastre uma nova transação de ativo para a sua carteira.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-2">
          <div className="space-y-1.5">
            <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Categoria</Label>
            <Select value={categoria} onValueChange={(value: string) => setCategoria(value as 'variavel' | 'fixa' | 'cripto')}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Selecione a categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="variavel">📈 Renda Variável (Ações, ETFs, FIIs)</SelectItem>
                <SelectItem value="fixa">📉 Renda Fixa (CDB, LCI, LCA, Tesouro)</SelectItem>
                <SelectItem value="cripto">₿ Criptomoedas (BTC, ETH)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {!isRendaFixa && (
            <>
              <div className="space-y-1.5">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  {isCripto ? 'Código da criptomoeda' : 'Ticker / Código'}
                </Label>
                <Input
                  value={ticker}
                  placeholder={isCripto ? 'Ex: BTC, ETH, SOL' : 'Ex: PETR4, VALE3'}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                />
              </div>
              <div className="space-y-1.5">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Quantidade</Label>
                <Input
                  type="number"
                  step="any"
                  placeholder="0.00"
                  value={quantidade}
                  onChange={(e) => setQuantidade(Number(e.target.value))}
                />
              </div>
            </>
          )}

          {isRendaFixa && (
            <>
              <div className="space-y-1.5">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Nome da aplicação</Label>
                <div className="relative">
                  <Tag className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    placeholder="Ex: CDB Inter 110% CDI"
                    value={nomeAplicacao}
                    onChange={(e) => setNomeAplicacao(e.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Valor aplicado (R$)</Label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    className="pl-9"
                    type="number"
                    step="any"
                    placeholder="0,00"
                    value={valorAplicado}
                    onChange={(e) => setValorAplicado(e.target.value)}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Data aplicação</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      className="pl-9"
                      type="date"
                      value={dataCompra}
                      onChange={(e) => setDataCompra(e.target.value)}
                    />
                  </div>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Data vencimento</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      className="pl-9"
                      type="date"
                      value={dataVencimento}
                      onChange={(e) => setDataVencimento(e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-secondary/30">
                <div className="flex items-center gap-2">
                  <Label className="text-sm font-medium">Possui carência?</Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="text-xs">Período mínimo para resgate sem penalidades.</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Switch checked={temCarencia} onCheckedChange={setTemCarencia} />
              </div>

              {temCarencia && (
                <div className="space-y-1.5 animate-in fade-in slide-in-from-top-1 duration-200">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Data limite da carência</Label>
                  <div className="relative">
                    <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      className="pl-9"
                      type="date"
                      value={dataCarencia}
                      onChange={(e) => setDataCarencia(e.target.value)}
                    />
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-1.5">
                    <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Tipo de ativo</Label>
                    <TooltipProvider>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
                        </TooltipTrigger>
                        <TooltipContent>
                          <p className="text-xs">{getIsencaoTooltip()}</p>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </div>
                  <Select
                    value={tipoAtivo}
                    onValueChange={(value: string) => setTipoAtivo(value as 'cdb' | 'lci' | 'lca' | 'tesouro')}
                  >
                    <SelectTrigger>
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

                <div className="space-y-1.5">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Indexador</Label>
                  <Select
                    value={indexador}
                    onValueChange={(value: string) => setIndexador(value as 'CDI' | 'IPCA' | 'PRE')}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="CDI">Pós‑fixado (CDI)</SelectItem>
                      <SelectItem value="IPCA">Híbrido (IPCA + taxa fixa)</SelectItem>
                      <SelectItem value="PRE">Pré‑fixado (taxa fixa anual)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-1.5">
                <div className="flex items-center gap-1.5">
                  <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                    {getTaxaLabel().label}
                  </Label>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Info className="h-3.5 w-3.5 text-muted-foreground cursor-help" />
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="text-xs">{getTaxaLabel().tip}</p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <Input
                  type="number"
                  step="any"
                  placeholder={getTaxaLabel().placeholder}
                  value={taxaContratada}
                  onChange={(e) => setTaxaContratada(e.target.value)}
                />
              </div>
            </>
          )}

          {!isRendaFixa && (
            <div className="space-y-1.5">
              <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Data da aplicação</Label>
              <Input type="date" value={dataCompra} onChange={(e) => setDataCompra(e.target.value)} />
            </div>
          )}

          <div className="space-y-1.5">
            <Label className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Plataforma</Label>
            <Select value={plataforma} onValueChange={setPlataforma}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {getPlataformas().map(p => (
                  <SelectItem key={p} value={p}>
                    {p === 'xp' ? 'XP Investimentos' : p.charAt(0).toUpperCase() + p.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {erro && (
            <div className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 border border-destructive/20 text-destructive text-sm">
              <AlertCircle className="h-4 w-4" />
              <span>{erro}</span>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:gap-0 border-t pt-4">
          <Button variant="outline" onClick={onClose} disabled={salvando}>
            Cancelar
          </Button>
          <Button onClick={salvar} disabled={salvando}>
            {salvando ? 'Salvando...' : 'Salvar aporte'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}