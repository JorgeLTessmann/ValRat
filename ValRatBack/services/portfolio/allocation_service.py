def gerar_allocations(
    assets,
    total_balance
):

    allocations_map = {}

    for asset in assets:

        tipo = asset["type"]

        if tipo not in allocations_map:

            allocations_map[tipo] = {

                "type": tipo,

                "label": tipo.upper(),

                "totalInvested": 0,

                "currentValue": 0
            }

        allocations_map[tipo][
            "totalInvested"
        ] += asset["totalInvested"]

        allocations_map[tipo][
            "currentValue"
        ] += asset["currentValue"]

    allocations = []

    for _, allocation in allocations_map.items():

        percentage = (
            (
                allocation["currentValue"] /
                total_balance
            ) * 100
            if total_balance > 0
            else 0
        )

        allocations.append({

            "type":
                allocation["type"],

            "label":
                allocation["label"],

            "totalInvested":
                round(
                    allocation["totalInvested"],
                    2
                ),

            "currentValue":
                round(
                    allocation["currentValue"],
                    2
                ),

            "percentage":
                round(
                    percentage,
                    2
                )
        })

    return allocations