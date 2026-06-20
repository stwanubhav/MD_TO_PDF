export function preprocessMarkdown(markdown: string): string {
  return markdown.replace(
    /(\[)(\s*)([^\[\]]+?)(\s*)(\])/g,
    (match, open, space1, content, space2, close) => {
      // Check if it's already a formula
      if (content.includes('$')) {
        return match;
      }
      // Convert [ ... ] to $$ ... $$
      return `$$${space1}${content}${space2}$$`;
    }
  );
}
