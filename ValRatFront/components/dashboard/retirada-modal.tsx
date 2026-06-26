'use client'

import { useEffect, useMemo, useState } from 'react'
import { useAuth } from '@/hooks/use-auth'

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from '@/components/ui/dialog'

import { Button } from '@/components/ui/button'

import { Input } from '@/components/ui/input'

import { Label } from '@/components/ui/label'

import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue
} from '@/components/ui/select'

interface Asset {
    ticker: string
    quantity: number
    currentPrice: number
}

interface Props {
    open: boolean
    onClose: () => void
    onSuccess: () => void
    assets?: Asset[]
}

export function RetiradaModal({
    open,
    onClose,
    onSuccess,
    assets
}: Props) {

    const { currentUser } = useAuth()

    const [ticker, setTicker] = useState('')
    const [quantidade, setQuantidade] = useState(1)

    const [erro, setErro] = useState('')
    const [salvando, setSalvando] = useState(false)

    // Agrupa os ativos por ticker, somando as cotas de todas as compras
    // (ex: 3 compras de PETR4 em momentos diferentes -> 1 entrada com o total).
    // Usado tanto para montar a lista do dropdown quanto para saber a
    // quantidade REAL disponível do ativo selecionado -- antes, cada um
    // desses dois pontos calculava isso de um jeito diferente, e por isso
    // a quantidade exibida não batia com o total agrupado.
    const ativosAgrupados = useMemo(() => {
        return (assets || []).reduce((acc, asset) => {
            if (!acc[asset.ticker]) {
                acc[asset.ticker] = {
                    ticker: asset.ticker,
                    quantity: 0,
                    currentPrice: asset.currentPrice
                }
            }

            acc[asset.ticker].quantity += asset.quantity

            return acc
        }, {} as Record<string, Asset>)
    }, [assets])

    const ativoSelecionado = useMemo(() => {

        return ativosAgrupados[ticker]

    }, [ativosAgrupados, ticker])

    useEffect(() => {

        setQuantidade(1)

    }, [ticker])

    const valorRetirada = useMemo(() => {

        if (!ativoSelecionado) {
            return 0
        }

        return (
            quantidade *
            ativoSelecionado.currentPrice
        )

    }, [quantidade, ativoSelecionado])

    const salvar = async () => {

        setErro('')

        if (!ticker) {
            setErro('Selecione um ativo')
            return
        }

        if (!ativoSelecionado) {
            setErro('Ativo inválido')
            return
        }

        if (quantidade <= 0) {
            setErro('Quantidade inválida')
            return
        }

        if (quantidade > ativoSelecionado.quantity) {
            setErro('Quantidade maior que posição atual')
            return
        }

        const userEmail = currentUser?.email ?? null

        if (!userEmail) {
            setErro('Usuário não identificado. Faça login novamente.')
            return
        }

        try {

            setSalvando(true)

            const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://valrat.onrender.com'

            const response = await fetch(
                `${baseUrl}/retiradas`,
                {
                    method: 'POST',

                    headers: {
                        'Content-Type': 'application/json',
                        'X-User-Email': userEmail
                    },

                    body: JSON.stringify({
                        ticker,
                        quantidade
                    })
                }
            )

            if (!response.ok) {

                const body =
                    await response.json()

                throw new Error(
                    body?.detail ||
                    'Erro ao retirar'
                )
            }

            onSuccess()
            onClose()

        } catch (error) {

            setErro(
                error instanceof Error
                    ? error.message
                    : 'Erro ao retirar'
            )

        } finally {

            setSalvando(false)
        }
    }

    return (
        <Dialog
            open={open}
            onOpenChange={(isOpen) => {
                if (!isOpen) onClose()
            }}
        >

            <DialogContent>

                <DialogHeader>

                    <DialogTitle>
                        Retirar ativo
                    </DialogTitle>

                    <DialogDescription>
                        Informe quantas ações deseja retirar.
                    </DialogDescription>

                </DialogHeader>

                <div className="grid gap-4">

                    <div className="grid gap-2">

                        <Label>Ativo</Label>

                        <Select
                            value={ticker}
                            onValueChange={setTicker}
                        >

                            <SelectTrigger>
                                <SelectValue placeholder="Selecione um ativo" />
                            </SelectTrigger>
                            <SelectContent>

                                {Object.values(ativosAgrupados).map((asset) => (

                                    <SelectItem
                                        key={asset.ticker}
                                        value={asset.ticker}
                                    >

                                        {asset.ticker}
                                        {' • '}
                                        {asset.quantity}
                                        {' cotas • R$ '}
                                        {asset.currentPrice.toFixed(2)}

                                    </SelectItem>

                                ))}

                            </SelectContent>

                        </Select>

                    </div>

                    {ativoSelecionado && (

                        <>
                            <div className="text-sm text-muted-foreground">

                                Quantidade disponível:
                                {' '}
                                <strong>
                                    {ativoSelecionado.quantity}
                                </strong>

                            </div>

                            <div className="text-sm text-muted-foreground">

                                Preço atual:
                                {' '}
                                <strong>
                                    {ativoSelecionado.currentPrice.toLocaleString(
                                        'pt-BR',
                                        {
                                            style: 'currency',
                                            currency: 'BRL'
                                        }
                                    )}
                                </strong>

                            </div>
                        </>

                    )}

                    <div className="grid gap-2">

                        <Label>
                            Quantidade
                        </Label>

                        <Input
                            type="number"
                            min={1}
                            max={
                                ativoSelecionado?.quantity || 1
                            }
                            value={quantidade}
                            onChange={(e) =>
                                setQuantidade(
                                    Number(e.target.value)
                                )
                            }
                        />

                    </div>

                    <div className="rounded-lg border p-3 bg-muted/30">

                        <p className="text-sm text-muted-foreground">
                            Valor estimado da retirada
                        </p>

                        <p className="text-xl font-bold">

                            {valorRetirada.toLocaleString(
                                'pt-BR',
                                {
                                    style: 'currency',
                                    currency: 'BRL'
                                }
                            )}

                        </p>

                    </div>

                    {erro && (
                        <p className="text-sm text-red-500">
                            {erro}
                        </p>
                    )}

                </div>

                <DialogFooter>

                    <Button
                        variant="outline"
                        onClick={onClose}
                    >
                        Cancelar
                    </Button>

                    <Button
                        onClick={salvar}
                        disabled={salvando}
                    >
                        {salvando
                            ? 'Processando...'
                            : 'Confirmar retirada'}
                    </Button>

                </DialogFooter>

            </DialogContent>

        </Dialog>
    )
}