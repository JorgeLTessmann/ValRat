'use client'

import {

  LineChart,

  Line,

  XAxis,

  YAxis,

  Tooltip,

  ResponsiveContainer,

  CartesianGrid,

  Legend

} from 'recharts'

import {

  Card,

  CardContent,

  CardHeader,

  CardTitle

} from '@/components/ui/card'


interface ComparisonItem {

  date: string

  carteira: number

  cdi: number

  ibov: number
}


interface Props {

  historico: ComparisonItem[]
}


export function PatrimonioChart({

  historico

}: Props) {

  const formatCurrency = (
    value: number
  ) => {

    return new Intl.NumberFormat(

      'pt-BR',

      {

        style: 'currency',

        currency: 'BRL',

        maximumFractionDigits: 0
      }

    ).format(value)
  }

  return (

    <Card className="
      border-border/50
      shadow-sm
    ">

      <CardHeader>

        <CardTitle>

          Performance da Carteira

        </CardTitle>

      </CardHeader>

      <CardContent>

        <div className="h-[400px]">

          <ResponsiveContainer
            width="100%"
            height="100%"
          >

            <LineChart
              data={historico}
            >

              <CartesianGrid
                strokeDasharray="3 3"
                opacity={0.15}
              />

              <XAxis

                dataKey="date"

                tick={{
                  fontSize: 12
                }}
              />

              <YAxis

                tickFormatter={
                  (value) =>
                    `R$ ${Math.round(value)}`
                }

                tick={{
                  fontSize: 12
                }}
              />

              <Tooltip

                formatter={(value) =>

                  formatCurrency(
                    Number(value)
                  )
                }

                contentStyle={{

                  borderRadius: '12px',

                  border: '1px solid #27272a',

                  backgroundColor: '#09090b'
                }}
              />

              <Legend />

              <Line

                type="monotone"

                dataKey="carteira"

                stroke="#3b82f6"

                strokeWidth={4}

                dot={false}

                name="Carteira"

                activeDot={{
                  r: 6
                }}
              />

              <Line

                type="monotone"

                dataKey="cdi"

                stroke="#22c55e"

                strokeWidth={2}

                dot={false}

                name="CDI"
              />

              <Line

                type="monotone"

                dataKey="ibov"

                stroke="#f59e0b"

                strokeWidth={2}

                dot={false}

                name="IBOV"
              />

            </LineChart>

          </ResponsiveContainer>

        </div>

      </CardContent>

    </Card>
  )
}