"use client";

import { useState } from "react";
import { TimeSeriesData } from "@/app/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ChartConfig, ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Brush } from 'recharts';
import { Activity } from "lucide-react";

interface TimeSeriesChartProps {
  data: TimeSeriesData[];
}

// Time range options for quick selection
const TIME_RANGES = [
  { label: '7D', days: 7 },
  { label: '1M', days: 30 },
  { label: 'ALL', days: null },
] as const;

// Chart configuration for shadcn/ui
const chartConfig = {
  price: {
    label: "ETF Price",
    color: "hsl(var(--chart-1))",
  },
} satisfies ChartConfig;

export function TimeSeriesChart({ data }: TimeSeriesChartProps) {
  // State to manage brush range
  const [brushRange, setBrushRange] = useState<{ startIndex: number; endIndex: number } | undefined>();
  const [activeRange, setActiveRange] = useState<string>('ALL');

  // Format date for display
  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Handle time range button click
  const handleTimeRangeClick = (label: string, days: number | null) => {
    setActiveRange(label);
    
    if (days === null) {
      // Show all data - explicitly set full range
      setBrushRange({ startIndex: 0, endIndex: data.length - 1 });
    } else {
      // Calculate range from the most recent date (rightmost)
      const endIndex = data.length - 1;
      const startIndex = Math.max(0, endIndex - days + 1);
      setBrushRange({ startIndex, endIndex });
    }
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
          <div className="flex gap-4">
            {/* Chart container */}
            <div className="flex-1">
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
                    startIndex={brushRange?.startIndex}
                    endIndex={brushRange?.endIndex}
                    onChange={(brushData) => {
                      // Update state when user manually drags the brush
                      if (brushData?.startIndex !== undefined && brushData?.endIndex !== undefined) {
                        setBrushRange({
                          startIndex: brushData.startIndex,
                          endIndex: brushData.endIndex
                        });
                        setActiveRange(''); // Clear active button when manually adjusted
                      }
                    }}
                  />
                </LineChart>
              </ChartContainer>
            </div>

            {/* Time range buttons */}
            <div className="flex flex-col gap-2 justify-center">
              {TIME_RANGES.map((range) => (
                <Button
                  key={range.label}
                  variant={activeRange === range.label ? "default" : "outline"}
                  size="sm"
                  onClick={() => handleTimeRangeClick(range.label, range.days)}
                  className="w-16"
                >
                  {range.label}
                </Button>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

