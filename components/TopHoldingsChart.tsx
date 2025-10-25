"use client";

import { TopHoldingData } from "@/app/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { BarChart3 } from "lucide-react";

interface TopHoldingsChartProps {
  data: TopHoldingData[];
}

// Chart configuration for shadcn/ui
const chartConfig = {
  holding_value: {
    label: "Holding Value",
    color: "hsl(var(--chart-2))", 
  },
} satisfies ChartConfig;

export function TopHoldingsChart({ data }: TopHoldingsChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Top 5 Holdings
        </CardTitle>
        <CardDescription>
          Largest holdings by market value (weight × price)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex h-[400px] items-center justify-center text-muted-foreground">
            No data available. Please upload an ETF file.
          </div>
        ) : (
          <ChartContainer config={chartConfig} className="h-[400px] w-full">
            <BarChart
              data={data}
              margin={{ top: 20, right: 10, left: 10, bottom: 0 }}
            >
              <CartesianGrid vertical={false} />
              <XAxis 
                dataKey="symbol" 
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis 
                tickLine={false}
                axisLine={false}
                tickMargin={8}
                tickFormatter={(value) => `$${value.toFixed(1)}`}
              />
              <ChartTooltip 
                content={
                  <ChartTooltipContent 
                    formatter={(value, name, props) => {
                      const data = props.payload;
                      return (
                        <div className="flex flex-col gap-1">
                          <div className="flex items-center gap-2">
                            <span className="font-semibold">${Number(value).toFixed(2)}</span>
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Weight: {(data.weight * 100).toFixed(2)}%
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Price: ${data.latest_price.toFixed(2)}
                          </div>
                        </div>
                      );
                    }}
                  />
                } 
              />
              <Bar 
                dataKey="holding_value" 
                fill="var(--color-holding_value)"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  );
}

