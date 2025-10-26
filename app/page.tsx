"use client";

import { useState } from "react";
import { FileUpload } from "@/components/FileUpload";
import { ETFTable } from "@/components/ETFTable";
import { TimeSeriesChart } from "@/components/TimeSeriesChart";
import { TopHoldingsChart } from "@/components/TopHoldingsChart";
import { ThemeToggle } from "@/components/theme-toggle";
import { ETFDataResponse } from "@/app/lib/types";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { AlertCircle, CheckCircle2, Upload } from "lucide-react";

export default function Home() {
  // State to hold ETF data
  const [etfData, setEtfData] = useState<ETFDataResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Handle successful upload
  const handleUploadSuccess = (data: ETFDataResponse) => {
    setEtfData(data);
    setError(null);
    setSuccess("ETF data loaded successfully!");
    
    // Clear success message after 5 seconds
    setTimeout(() => setSuccess(null), 5000);
  };

  // Handle upload error
  const handleUploadError = (errorMessage: string) => {
    setError(errorMessage);
    setSuccess(null);
    
    // Clear error message after 5 seconds
    setTimeout(() => setError(null), 5000);
  };

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">ETF Price Monitor</h1>
              <p className="text-muted-foreground mt-2">
                Upload ETF configuration to view historical prices and top holdings
              </p>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* File Upload Section */}
          <FileUpload 
            onUploadSuccess={handleUploadSuccess}
            onUploadError={handleUploadError}
          />

          {/* Success Message */}
          {success && (
            <Alert className="border-green-200 bg-green-50 text-green-900 dark:border-green-800 dark:bg-green-950 dark:text-green-100">
              <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Error Message */}
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Data Visualization Section */}
          {etfData && (
            <>
              {/* ETF Table */}
              <ETFTable data={etfData.table_data} />

              {/* Charts Grid */}
              <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-2">
                {/* Time Series Chart */}
                <div className="lg:col-span-2">
                  <TimeSeriesChart data={etfData.time_series} />
                </div>

                {/* Top Holdings Chart */}
                <div className="lg:col-span-2">
                  <TopHoldingsChart data={etfData.top_holdings} />
                </div>
              </div>
            </>
          )}

          {/* Empty State */}
          {!etfData && !error && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="rounded-full bg-muted p-6 mb-4">
                <Upload className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-semibold mb-2">No ETF data loaded</h3>
              <p className="text-muted-foreground max-w-md">
                Upload an ETF configuration file (CSV) to view historical prices, 
                constituent details, and top holdings analysis.
              </p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
