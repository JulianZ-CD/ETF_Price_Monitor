"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Upload, FileText } from "lucide-react";
import { API_ENDPOINTS, API_ERRORS } from "@/lib/api-config";

interface FileUploadProps {
  onUploadSuccess: (data: any) => void;
  onUploadError: (error: string) => void;
}

export function FileUpload({ onUploadSuccess, onUploadError }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Validate file type
      if (!selectedFile.name.endsWith('.csv')) {
        onUploadError(API_ERRORS.INVALID_FILE);
        return;
      }
      
      setFile(selectedFile);
    }
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      onUploadError('Please select a file first');
      return;
    }

    setIsUploading(true);

    try {
      // Create FormData to send file
      const formData = new FormData();
      formData.append('file', file);

      // Send to backend API using centralized endpoint configuration
      // Benefits:
      // - No hardcoded URLs
      // - Uses Next.js rewrites for proxy
      // - Easy to update when API changes
      // - Type-safe endpoint reference
      const response = await fetch(API_ENDPOINTS.ETF.CREATE_ANALYSIS, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || API_ERRORS.UPLOAD_FAILED);
      }

      const data = await response.json();
      onUploadSuccess(data);
      
      // Reset file input
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      // Handle different types of errors
      if (error instanceof TypeError && error.message.includes('fetch')) {
        onUploadError(API_ERRORS.NETWORK_ERROR);
      } else {
        onUploadError(error instanceof Error ? error.message : API_ERRORS.UPLOAD_FAILED);
      }
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Upload ETF Configuration
        </CardTitle>
        <CardDescription>
          Upload a CSV file containing ETF constituents and their weights
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <Input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileChange}
              disabled={isUploading}
              className="cursor-pointer"
            />
          </div>
          <Button 
            onClick={handleUpload} 
            disabled={!file || isUploading}
            className="min-w-[100px]"
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </Button>
        </div>
        
        {file && (
          <div className="mt-4 flex items-center gap-2 text-sm text-muted-foreground">
            <FileText className="h-4 w-4" />
            <span>Selected: {file.name}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

