import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface EditorState {
  markdown: string;
  theme: 'light' | 'dark';
  setMarkdown: (markdown: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  toggleTheme: () => void;
  newDocument: () => void;
}

const initialMarkdown = `# Welcome to Markdown to Beautiful PDF Studio

## Features
- **Live Preview**: See your Markdown rendered in real-time
- **Formula Support**: Convert ChatGPT formulas \`[ ... ]\` to KaTeX automatically
- **Beautiful PDF**: Generate professional PDFs with cover pages and TOC
- **Dark/Light Theme**: Toggle between themes
- **Export Options**: PDF, HTML, and Markdown export

## Getting Started
1. Type or paste your Markdown content here
2. See the live preview on the right
3. Download as PDF or export in other formats

## Example with Formula
\`\`\`
[ E = mc^2 ]
\`\`\`

Enjoy writing beautiful documents!`;

export const useEditorStore = create<EditorState>()(
  persist(
    (set) => ({
      markdown: initialMarkdown,
      theme: 'light',
      setMarkdown: (markdown) => set({ markdown }),
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),
      newDocument: () => set({ markdown: '' }),
    }),
    {
      name: 'editor-store',
    }
  )
);
