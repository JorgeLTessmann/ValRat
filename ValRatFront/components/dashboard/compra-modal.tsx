'use client'

import { useState } from 'react'

import { Plus } from 'lucide-react'

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

interface Props {
    open: boolean
    onClose: () => void
    onSuccess: () => void
}

function hojeISO() {

    return new Date()
        .toISOString()
        .slice(0, 10)
}

export function CompraModal({
    open,
    onClose,
    onSuccess
}: Props) {

    const [ticker, setTicker] =
        useState('')

    const [nome, setNome] =
        useState('')

    const [tipo, setTipo] =
        useState('acao')

    const [plataforma, setPlataforma] =
        useState('xp')

    const [quantidade, setQuantidade] =
        useState(1)

    const [valorAplicado, setValorAplicado] =
        useState('')

    const [indexador, setIndexador] =
        useState('CDI')

    const [taxa, setTaxa] =
        useState('')

    const [dataVencimento, setDataVencimento] =
        useState('')

    const [dataCompra, setDataCompra] =
        useState(hojeISO())

    const [erro, setErro] =
        useState('')

    const [salvando, setSalvando] =
        useState(false)

    const rendaFixaTypes = [
        'cdb',
        'lci',
        'lca',
        'fundo'
    ]

    const isRendaFixa =
        rendaFixaTypes.includes(tipo)

    const salvar = async () => {

        setErro('')
        setSalvando(true)

        try {

            let response

            if (isRendaFixa) {

                response = await fetch(
                    'http://127.0.0.1:8000/renda-fixa',
                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body: JSON.stringify({

                            nome,

                            tipo,

                            indexador,

                            taxa:
                                Number(taxa),

                            valor_aplicado:
                                Number(valorAplicado),

                            data_aplicacao:
                                dataCompra,

                            data_vencimento:
                                dataVencimento,

                            plataforma
                        })
                    }
                )

            } else {

                response = await fetch(
                    'http://127.0.0.1:8000/compras',
                    {
                        method: 'POST',

                        headers: {
                            'Content-Type':
                                'application/json'
                        },

                        body: JSON.stringify({

                            ticker:
                                ticker
                                    .trim()
                                    .toUpperCase(),

                            tipo,

                            plataforma,

                            quantidade,

                            data:
                                dataCompra
                        })
                    }
                )
            }

            const body =
                await response
                    .json()
                    .catch(() => null)

            if (!response.ok) {

                const msg =
                    body?.erro ||
                    body?.detail ||
                    'Erro ao salvar'

                throw new Error(msg)
            }

            if (body?.erro) {

                throw new Error(
                    body.erro
                )
            }

            setTicker('')
            setNome('')
            setTipo('acao')
            setPlataforma('xp')
            setQuantidade(1)
            setValorAplicado('')
            setIndexador('CDI')
            setTaxa('')
            setDataVencimento('')
            setDataCompra(hojeISO())

            onSuccess()

            onClose()

        } catch (error) {

            setErro(
                error instanceof Error
                    ? error.message
                    : 'Erro ao salvar'
            )

        } finally {

            setSalvando(false)
        }
    }

    return (
        <Dialog
            open={open}
            onOpenChange={(isOpen) => {

                if (!isOpen) {
                    onClose()
                }
            }}
        >
            <DialogContent
                className="
                    border-border/50
                    sm:max-w-md
                    gap-5
                "
            >

                <DialogHeader>

                    <DialogTitle
                        className="
                            flex
                            items-center
                            gap-2
                            text-accent-foreground
                        "
                    >

                        <span
                            className="
                                flex
                                h-8
                                w-8
                                items-center
                                justify-center
                                rounded-full
                                bg-accent
                            "
                        >

                            <Plus
                                className="
                                    h-4
                                    w-4
                                    text-primary
                                "
                            />

                        </span>

                        Novo aporte

                    </DialogTitle>

                    <DialogDescription>

                        Cadastre um novo ativo
                        na carteira.

                    </DialogDescription>

                </DialogHeader>

                <div className="grid gap-4">

                    <div className="grid gap-2">

                        <Label htmlFor="compra-tipo">
                            Tipo do ativo
                        </Label>

                        <Select
                            value={tipo}
                            onValueChange={setTipo}
                        >

                            <SelectTrigger
                                id="compra-tipo"
                                className="w-full"
                            >

                                <SelectValue />

                            </SelectTrigger>

                            <SelectContent>

                                <SelectItem value="acao">
                                    Ação
                                </SelectItem>

                                <SelectItem value="fii">
                                    FII
                                </SelectItem>

                                <SelectItem value="etf">
                                    ETF
                                </SelectItem>

                                <SelectItem value="cdb">
                                    CDB
                                </SelectItem>

                                <SelectItem value="lci">
                                    LCI
                                </SelectItem>

                                <SelectItem value="lca">
                                    LCA
                                </SelectItem>

                                <SelectItem value="fundo">
                                    Fundo
                                </SelectItem>

                            </SelectContent>

                        </Select>

                    </div>

                    <div className="grid gap-2">

                        <Label htmlFor="compra-plataforma">
                            Plataforma
                        </Label>

                        <Select
                            value={plataforma}
                            onValueChange={setPlataforma}
                        >

                            <SelectTrigger
                                id="compra-plataforma"
                                className="w-full"
                            >

                                <SelectValue />

                            </SelectTrigger>

                            <SelectContent>

                                <SelectItem value="xp">
                                    XP Investimentos
                                </SelectItem>

                                <SelectItem value="inter">
                                    Banco Inter
                                </SelectItem>

                                <SelectItem value="itau">
                                    Itaú
                                </SelectItem>

                                <SelectItem value="nubank">
                                    Nubank
                                </SelectItem>

                                <SelectItem value="clear">
                                    Clear
                                </SelectItem>

                                <SelectItem value="rico">
                                    Rico
                                </SelectItem>

                            </SelectContent>

                        </Select>

                    </div>

                    <div className="grid gap-2">

                        <Label htmlFor="compra-data">
                            Data da aplicação
                        </Label>

                        <Input
                            id="compra-data"

                            type="date"

                            value={dataCompra}

                            onChange={(e) =>
                                setDataCompra(
                                    e.target.value
                                )
                            }
                        />

                    </div>

                    {!isRendaFixa && (

                        <>
                            <div className="grid gap-2">

                                <Label htmlFor="compra-ticker">
                                    Ticker
                                </Label>

                                <Input
                                    id="compra-ticker"

                                    placeholder="Ex: PETR4"

                                    value={ticker}

                                    onChange={(e) =>
                                        setTicker(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>

                            <div className="grid gap-2">

                                <Label htmlFor="compra-quantidade">
                                    Quantidade
                                </Label>

                                <Input
                                    id="compra-quantidade"

                                    type="number"

                                    min={1}

                                    value={quantidade}

                                    onChange={(e) =>
                                        setQuantidade(
                                            Number(
                                                e.target.value
                                            )
                                        )
                                    }
                                />

                            </div>
                        </>

                    )}

                    {isRendaFixa && (

                        <>
                            <div className="grid gap-2">

                                <Label>
                                    Nome do produto
                                </Label>

                                <Input
                                    placeholder="Ex: CDB Inter 110 CDI"

                                    value={nome}

                                    onChange={(e) =>
                                        setNome(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>

                            <div className="grid gap-2">

                                <Label>
                                    Valor aplicado
                                </Label>

                                <Input
                                    type="number"

                                    value={valorAplicado}

                                    onChange={(e) =>
                                        setValorAplicado(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>

                            <div className="grid gap-2">

                                <Label>
                                    Indexador
                                </Label>

                                <Select
                                    value={indexador}
                                    onValueChange={
                                        setIndexador
                                    }
                                >

                                    <SelectTrigger>

                                        <SelectValue />

                                    </SelectTrigger>

                                    <SelectContent>

                                        <SelectItem value="CDI">
                                            CDI
                                        </SelectItem>

                                        <SelectItem value="IPCA">
                                            IPCA
                                        </SelectItem>

                                        <SelectItem value="PRE">
                                            Prefixado
                                        </SelectItem>

                                    </SelectContent>

                                </Select>

                            </div>

                            <div className="grid gap-2">

                                <Label>
                                    Taxa
                                </Label>

                                <Input
                                    type="number"

                                    placeholder="Ex: 110"

                                    value={taxa}

                                    onChange={(e) =>
                                        setTaxa(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>

                            <div className="grid gap-2">

                                <Label>
                                    Vencimento
                                </Label>

                                <Input
                                    type="date"

                                    value={dataVencimento}

                                    onChange={(e) =>
                                        setDataVencimento(
                                            e.target.value
                                        )
                                    }
                                />

                            </div>
                        </>

                    )}

                    {erro && (

                        <p
                            className="
                                text-sm
                                text-destructive
                            "
                        >
                            {erro}
                        </p>

                    )}

                </div>

                <DialogFooter
                    className="
                        gap-2
                        sm:gap-2
                    "
                >

                    <Button
                        type="button"

                        variant="outline"

                        onClick={onClose}

                        disabled={salvando}
                    >
                        Cancelar
                    </Button>

                    <Button
                        type="button"

                        onClick={salvar}

                        disabled={salvando}
                    >

                        {salvando
                            ? 'Salvando...'
                            : 'Salvar'}

                    </Button>

                </DialogFooter>

            </DialogContent>
        </Dialog>
    )
}