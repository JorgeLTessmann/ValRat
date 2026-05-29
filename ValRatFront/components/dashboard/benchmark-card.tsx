'use client'

import {

  Card,

  CardContent,

  CardHeader,

  CardTitle

} from '@/components/ui/card'


interface BenchmarkProps {

  carteira: number

  cdi: number

  selic: number

  ibov: number
}


export function BenchmarkCard({

  carteira,

  cdi,

  selic,

  ibov

}: BenchmarkProps) {

  const benchmarks = [

    {

      label: 'Carteira',

      value: carteira
    },

    {

      label: 'CDI',

      value: cdi
    },

    {

      label: 'SELIC',

      value: selic
    },

    {

      label: 'IBOV',

      value: ibov
    }
  ]


  return (

    <Card>

      <CardHeader>

        <CardTitle>

          Benchmark

        </CardTitle>

      </CardHeader>

      <CardContent>

        <div className="space-y-4">

          {benchmarks.map((item) => (

            <div
              key={item.label}
              className="
                flex
                items-center
                justify-between
              "
            >

              <span className="text-sm text-muted-foreground">

                {item.label}

              </span>

              <span
                className={`
                  font-bold
                  ${
                    item.value >= 0

                    ? 'text-green-500'

                    : 'text-red-500'
                  }
                `}
              >

                {item.value.toFixed(2)}%

              </span>

            </div>
          ))}

        </div>

      </CardContent>

    </Card>
  )
}