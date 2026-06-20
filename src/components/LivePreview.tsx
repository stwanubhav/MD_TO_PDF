'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';
import { preprocessMarkdown } from '@/utils/math';

interface LivePreviewProps {
  markdown: string;
  theme: 'light' | 'dark';
}

export default function LivePreview({ markdown, theme }: LivePreviewProps) {
  const processedMarkdown = preprocessMarkdown(markdown);

  const components = {
    h1: ({ children }: any) => (
      <h1 className="text-4xl font-bold mt-6 mb-4 text-gray-900 dark:text-white">{children}</h1>
    ),
    h2: ({ children }: any) => (
      <h2 className="text-3xl font-bold mt-5 mb-3 text-gray-800 dark:text-gray-100">{children}</h2>
    ),
    h3: ({ children }: any) => (
      <h3 className="text-2xl font-bold mt-4 mb-2 text-gray-700 dark:text-gray-200">{children}</h3>
    ),
    h4: ({ children }: any) => (
      <h4 className="text-xl font-bold mt-3 mb-2 text-gray-700 dark:text-gray-200">{children}</h4>
    ),
    p: ({ children }: any) => (
      <p className="text-base leading-7 mb-4 text-gray-700 dark:text-gray-300">{children}</p>
    ),
    a: ({ href, children }: any) => (
      <a href={href} className="text-blue-600 dark:text-blue-400 underline hover:text-blue-800 dark:hover:text-blue-300">
        {children}
      </a>
    ),
    img: ({ src, alt }: any) => (
      <img src={src} alt={alt} className="max-w-full h-auto rounded-lg my-4 shadow-md" />
    ),
    code: ({ inline, children }: any) => (
      inline ? (
        <code className="bg-gray-200 dark:bg-slate-800 px-2 py-1 rounded font-mono text-sm text-gray-900 dark:text-gray-100">
          {children}
        </code>
      ) : (
        <code className="block bg-gray-900 dark:bg-slate-900 text-gray-100 p-4 rounded-lg overflow-x-auto font-mono text-sm mb-4">
          {children}
        </code>
      )
    ),
    pre: ({ children }: any) => <pre className="overflow-x-auto">{children}</pre>,
    table: ({ children }: any) => (
      <table className="border-collapse w-full my-4 border border-gray-300 dark:border-gray-600">
        {children}
      </table>
    ),
    th: ({ children }: any) => (
      <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-100 dark:bg-slate-800 font-semibold text-left">
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td className="border border-gray-300 dark:border-gray-600 px-4 py-2">{children}</td>
    ),
    blockquote: ({ children }: any) => (
      <blockquote className="border-l-4 border-gray-400 dark:border-gray-600 pl-4 py-1 my-4 italic text-gray-600 dark:text-gray-400">
        {children}
      </blockquote>
    ),
    ul: ({ children }: any) => (
      <ul className="list-disc list-inside mb-4 text-gray-700 dark:text-gray-300">{children}</ul>
    ),
    ol: ({ children }: any) => (
      <ol className="list-decimal list-inside mb-4 text-gray-700 dark:text-gray-300">{children}</ol>
    ),
    li: ({ children }: any) => (
      <li className="mb-2">{children}</li>
    ),
    hr: () => (
      <hr className="my-6 border-gray-300 dark:border-gray-600" />
    ),
  };

  return (
    <div className={`p-8 ${theme === 'dark' ? 'bg-slate-950 text-white' : 'bg-white text-gray-900'}`}>
      <div className="prose dark:prose-invert max-w-none">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeKatex]}
          components={components}
        >
          {processedMarkdown}
        </ReactMarkdown>
      </div>
    </div>
  );
}
