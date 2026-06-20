'use client';

import React from 'react';
import Editor from '@monaco-editor/react';

interface MonacoEditorProps {
  value: string;
  onChange: (value: string) => void;
}

export default function MonacoEditor({ value, onChange }: MonacoEditorProps) {
  return (
    <Editor
      height="100%"
      defaultLanguage="markdown"
      defaultValue={value}
      value={value}
      onChange={(val) => onChange(val || '')}
      theme="vs-dark"
      options={{
        minimap: { enabled: false },
        wordWrap: 'on',
        fontSize: 14,
        automaticLayout: true,
        scrollBeyondLastLine: false,
      }}
    />
  );
}
