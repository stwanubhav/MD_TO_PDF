'use client';

import React, { useRef } from 'react';
import {
  FileUp,
  FileX,
  Save,
  FileJson,
  Printer,
  Code,
  FileText,
  Copy,
  Moon,
  Settings,
  Maximize2,
} from 'lucide-react';

interface ToolbarProps {
  onUpload: (content: string) => void;
  onNew: () => void;
  onSave: () => void;
  onDownloadPDF: () => void;
  onPrint: () => void;
  onExportHTML: () => void;
  onExportMarkdown: () => void;
  onCopyHTML: () => void;
  onCopyMarkdown: () => void;
  onToggleTheme: () => void;
  onOpenSettings: () => void;
  onFullscreen: () => void;
}

export default function Toolbar({
  onUpload,
  onNew,
  onSave,
  onDownloadPDF,
  onPrint,
  onExportHTML,
  onExportMarkdown,
  onCopyHTML,
  onCopyMarkdown,
  onToggleTheme,
  onOpenSettings,
  onFullscreen,
}: ToolbarProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const content = await file.text();
      onUpload(content);
    }
  };

  return (
    <div className="flex items-center gap-2 bg-white dark:bg-slate-900 border-b border-gray-200 dark:border-slate-800 px-4 py-3 flex-wrap">
      <input
        ref={fileInputRef}
        type="file"
        accept=".md,.markdown,.txt"
        onChange={handleFileSelect}
        className="hidden"
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Upload"
      >
        <FileUp size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onNew}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="New"
      >
        <FileX size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onSave}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Save as Markdown"
      >
        <Save size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onDownloadPDF}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Download PDF"
      >
        <FileJson size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onPrint}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Print"
      >
        <Printer size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onExportHTML}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Export HTML"
      >
        <Code size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onExportMarkdown}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Export Markdown"
      >
        <FileText size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onCopyHTML}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Copy HTML"
      >
        <Copy size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onCopyMarkdown}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Copy Markdown"
      >
        <Copy size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <div className="flex-1" />

      <button
        onClick={onToggleTheme}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Toggle Theme"
      >
        <Moon size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onOpenSettings}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Settings"
      >
        <Settings size={20} className="text-gray-700 dark:text-gray-300" />
      </button>

      <button
        onClick={onFullscreen}
        className="p-2 hover:bg-gray-100 dark:hover:bg-slate-800 rounded transition"
        title="Fullscreen"
      >
        <Maximize2 size={20} className="text-gray-700 dark:text-gray-300" />
      </button>
    </div>
  );
}
