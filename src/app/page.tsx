'use client';

import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import Toolbar from '@/components/Toolbar';
import LivePreview from '@/components/LivePreview';
import { useEditorStore } from '@/store/editorStore';
import { downloadFile, copyToClipboard } from '@/utils/export';
import { generatePDFHTML } from '@/utils/pdf';

const MonacoEditor = dynamic(
  () => import('@/components/MonacoEditor'),
  {
    ssr: false,
    loading: () => <div className="flex items-center justify-center">Loading editor...</div>,
  }
);

export default function Home() {
  const { markdown, theme, setMarkdown, toggleTheme, newDocument } = useEditorStore();
  const [isClient, setIsClient] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleUpload = (content: string) => {
    setMarkdown(content);
  };

  const handleNew = () => {
    if (confirm('Create a new document? Any unsaved changes will be lost.')) {
      newDocument();
    }
  };

  const handleSave = () => {
    downloadFile(markdown, 'document.md', 'text/markdown');
  };

  const handleDownloadPDF = async () => {
    setIsLoading(true);
    try {
      const htmlContent = await generatePDFHTML(markdown);
      const response = await fetch('/api/generate-pdf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ html: htmlContent }),
      });

      if (!response.ok) throw new Error('PDF generation failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'document.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('PDF generation error:', error);
      alert('Failed to generate PDF. Check console for details.');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  const handleExportHTML = async () => {
    const htmlContent = await generatePDFHTML(markdown);
    downloadFile(htmlContent, 'document.html', 'text/html');
  };

  const handleExportMarkdown = () => {
    downloadFile(markdown, 'document.md', 'text/markdown');
  };

  const handleCopyHTML = async () => {
    const htmlContent = await generatePDFHTML(markdown);
    await copyToClipboard(htmlContent);
    alert('HTML copied to clipboard!');
  };

  const handleCopyMarkdown = async () => {
    await copyToClipboard(markdown);
    alert('Markdown copied to clipboard!');
  };

  const handleToggleTheme = () => {
    toggleTheme();
  };

  const handleOpenSettings = () => {
    alert('Settings modal coming soon!');
  };

  const handleFullscreen = () => {
    const editorContainer = document.getElementById('editor-container');
    if (editorContainer?.requestFullscreen) {
      editorContainer.requestFullscreen();
    }
  };

  if (!isClient) {
    return null;
  }

  return (
    <div className={`flex flex-col h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <Toolbar
        onUpload={handleUpload}
        onNew={handleNew}
        onSave={handleSave}
        onDownloadPDF={handleDownloadPDF}
        onPrint={handlePrint}
        onExportHTML={handleExportHTML}
        onExportMarkdown={handleExportMarkdown}
        onCopyHTML={handleCopyHTML}
        onCopyMarkdown={handleCopyMarkdown}
        onToggleTheme={handleToggleTheme}
        onOpenSettings={handleOpenSettings}
        onFullscreen={handleFullscreen}
      />

      <div className="flex flex-1 gap-0 overflow-hidden bg-white dark:bg-slate-950">
        <div id="editor-container" className="w-1/2 border-r border-gray-200 dark:border-slate-800">
          <MonacoEditor value={markdown} onChange={setMarkdown} />
        </div>

        <div className="w-1/2 overflow-auto bg-white dark:bg-slate-950">
          <LivePreview markdown={markdown} theme={theme} />
        </div>
      </div>

      {isLoading && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-slate-900 px-8 py-6 rounded-lg shadow-lg">
            <p className="text-gray-800 dark:text-gray-200">Generating PDF...</p>
          </div>
        </div>
      )}
    </div>
  );
}
