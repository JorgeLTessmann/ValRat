from services.portfolio_service import montar_portfolio
result = montar_portfolio(force_refresh=True)
print(f'Resultado do montar_portfolio: {result["totalBalance"]}')
print(f'Assets: {len(result["assets"])}')
if result["assets"]:
    print(f'Primeiro asset: {result["assets"][0]}')