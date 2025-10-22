"use client";

import { useState, useMemo } from "react";
import { ConstituentData } from "@/lib/types";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { TrendingUp, ArrowUpDown, ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from "lucide-react";

interface ETFTableProps {
  data: ConstituentData[];
}

type SortField = 'symbol' | 'weight' | 'latest_price';
type SortOrder = 'asc' | 'desc';

export function ETFTable({ data }: ETFTableProps) {
  // Sorting state
  const [sortField, setSortField] = useState<SortField>('symbol');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Format number to fixed decimal places
  const formatNumber = (num: number, decimals: number = 2): string => {
    return num.toFixed(decimals);
  };

  // Format weight as percentage
  const formatWeight = (weight: number): string => {
    return `${(weight * 100).toFixed(2)}%`;
  };

  // Handle sort
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      // Toggle sort order if same field
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // New field: symbol defaults to asc, numeric fields default to desc
      setSortField(field);
      setSortOrder(field === 'symbol' ? 'asc' : 'desc');
    }
    // Reset to first page when sorting
    setCurrentPage(1);
  };

  // Sort icon component
  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) {
      return <ArrowUpDown className="ml-2 h-4 w-4" />;
    }
    return sortOrder === 'asc' ? 
      <ArrowUp className="ml-2 h-4 w-4" /> : 
      <ArrowDown className="ml-2 h-4 w-4" />;
  };

  // Sorted and paginated data
  const sortedData = useMemo(() => {
    const sorted = [...data].sort((a, b) => {
      let aValue: number | string;
      let bValue: number | string;

      switch (sortField) {
        case 'symbol':
          aValue = a.symbol;
          bValue = b.symbol;
          break;
        case 'weight':
          aValue = a.weight;
          bValue = b.weight;
          break;
        case 'latest_price':
          aValue = a.latest_price;
          bValue = b.latest_price;
          break;
      }

      if (typeof aValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue as string)
          : (bValue as string).localeCompare(aValue);
      } else {
        return sortOrder === 'asc' 
          ? (aValue as number) - (bValue as number)
          : (bValue as number) - (aValue as number);
      }
    });

    return sorted;
  }, [data, sortField, sortOrder]);

  // Calculate pagination
  const totalPages = Math.ceil(sortedData.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedData = sortedData.slice(startIndex, endIndex);

  // Pagination handlers
  const goToNextPage = () => {
    setCurrentPage((page) => Math.min(page + 1, totalPages));
  };

  const goToPreviousPage = () => {
    setCurrentPage((page) => Math.max(page - 1, 1));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          ETF Constituents
        </CardTitle>
        <CardDescription>
          All constituents with their weights and latest prices
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-[100px]">
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('symbol')}
                    className="h-8 px-2 lg:px-3"
                  >
                    Symbol
                    <SortIcon field="symbol" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('weight')}
                    className="h-8 px-2 lg:px-3"
                  >
                    Weight
                    <SortIcon field="weight" />
                  </Button>
                </TableHead>
                <TableHead className="text-right">
                  <Button
                    variant="ghost"
                    onClick={() => handleSort('latest_price')}
                    className="h-8 px-2 lg:px-3"
                  >
                    Latest Price
                    <SortIcon field="latest_price" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={3} className="h-24 text-center text-muted-foreground">
                    No data available. Please upload an ETF file.
                  </TableCell>
                </TableRow>
              ) : (
                paginatedData.map((row) => (
                  <TableRow key={row.symbol}>
                    <TableCell className="font-medium">{row.symbol}</TableCell>
                    <TableCell className="text-right">{formatWeight(row.weight)}</TableCell>
                    <TableCell className="text-right">${formatNumber(row.latest_price)}</TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </div>
        
        {/* Pagination and info */}
        {data.length > 0 && (
          <div className="flex items-center justify-between mt-4">
            <div className="text-sm text-muted-foreground">
              Showing {startIndex + 1} to {Math.min(endIndex, data.length)} of {data.length} constituents
            </div>
            
            {totalPages > 1 && (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToPreviousPage}
                  disabled={currentPage === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <div className="text-sm text-muted-foreground">
                  Page {currentPage} of {totalPages}
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

