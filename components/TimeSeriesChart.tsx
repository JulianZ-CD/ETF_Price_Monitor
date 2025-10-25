"use client";

import { TimeSeriesData } from "@/app/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Brush } from 'recharts';
import { Activity } from "lucide-react";

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
}

// Chart configuration for shadcn/ui
const chartConfig = {
  price: {
    label: "ETF Price",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig;

export function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  // Format date for display
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Activity className="h-5 w-5" />
          ETF Price History
        </CardTitle>
        <CardDescription>
          Historical reconstructed price based on weighted constituents
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <div className="flex h-[400px] items-center justify-center text-muted-foreground">
            No data available. Please upload an ETF file.
          </div>
        ) : (
          <ChartContainer config={chartConfig} className="h-[450px] w-full">
            <LineChart
              data={data}
              margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
            >
              <CartesianGrid vertical={false} />
              <XAxis 
                dataKey="date" 
                tickFormatter={formatDate}
                tickLine={false}
                axisLine={false}
                tickMargin={8}
              />
              <YAxis 
                tickLine={false}
                axisLine={false}
                domain={['auto', 'auto']}
                tickMargin={8}
                tickFormatter={(value) => `$${value.toFixed(0)}`}
              />
              <ChartTooltip 
                content={
                  <ChartTooltipContent 
                    formatter={(value) => `$${Number(value).toFixed(2)}`}
                    labelFormatter={(label) => label}
                  />
                } 
              />
              <Line 
                type="monotone" 
                dataKey="price" 
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6 }}
              />
              {/* Brush component for zoomable time range selection */}
              <Brush 
                dataKey="date"
                height={50}
                tickFormatter={formatDate}
              />
            </LineChart>
          </ChartContainer>
        )}
      </CardContent>
    </Card>
  );
}

