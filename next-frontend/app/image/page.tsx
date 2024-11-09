'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, File, Info } from 'lucide-react'
import Image from 'next/image'

export default function Component() {
  const [file, setFile] = useState<File | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop })

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }
  return (
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8 flex items-center justify-between">
            <div className='flex flex-row items-center'>
        <Image src="/logo.png" alt="Logo" width={50} height={50} />
          <h1 className="text-2xl font-semibold text-gray-900">LlamaVision</h1>
          </div>
          <Button variant="outline">Logout</Button>
        </div>
      </header>

      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Card className="w-full max-w-2xl mx-auto">
          <CardHeader>
            <CardTitle>File Upload</CardTitle>
            <CardDescription>Upload a file to view its details</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                isDragActive ? 'border-primary bg-primary/10' : 'border-gray-300 hover:border-primary'
              }`}
            >
              <input {...getInputProps()} />
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                Drag 'n' drop a file here, or click to select a file
              </p>
            </div>

            {file && (
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">File Information</h3>
                {file.type.startsWith('image/') && (
                  <div className="mb-4">
                    <img
                      src={URL.createObjectURL(file)}
                      alt="Uploaded file preview"
                      className="max-w-full h-auto rounded-lg shadow-md"
                    />
                  </div>
                )}
                <div className="grid gap-4">
                  <div className="flex items-center">
                    <File className="mr-2 h-4 w-4" />
                    <span className="font-medium">Name:</span>
                    <span className="ml-2">{file.name}</span>
                  </div>
                  <div className="flex items-center">
                    <Info className="mr-2 h-4 w-4" />
                    <span className="font-medium">Type:</span>
                    <span className="ml-2">{file.type || 'Unknown'}</span>
                  </div>
                  <div className="flex items-center">
                    <Upload className="mr-2 h-4 w-4" />
                    <span className="font-medium">Size:</span>
                    <span className="ml-2">{formatFileSize(file.size)}</span>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-between">
            <Button variant="outline" onClick={() => setFile(null)} disabled={!file}>
              Clear
            </Button>
            <Button disabled={!file}>Process File</Button>
          </CardFooter>
        </Card>
      </main>

      <footer className="bg-white border-t">
        <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            © 2024 LlamaVision
          </p>
        </div>
      </footer>
    </div>
  )
}