def calcular_valor_investido(
    preco_compra,
    quantidade
):

    return preco_compra * quantidade



def calcular_valor_atual(
    preco_atual,
    quantidade
):

    return preco_atual * quantidade



def calcular_resultado(
    valor_atual,
    valor_investido
):

    return valor_atual - valor_investido



def calcular_variacao(
    resultado,
    valor_investido
):

    return (
        resultado / valor_investido
    ) * 100



def calcular_posicao(
    preco_compra,
    preco_atual,
    quantidade
):

    valor_investido = (
        calcular_valor_investido(
            preco_compra,
            quantidade
        )
    )

    valor_atual = (
        calcular_valor_atual(
            preco_atual,
            quantidade
        )
    )

    resultado = calcular_resultado(
        valor_atual,
        valor_investido
    )

    variacao = calcular_variacao(
        resultado,
        valor_investido
    )

    return {

        "valor_investido": valor_investido,

        "valor_atual": valor_atual,

        "resultado": resultado,

        "variacao": variacao
    }