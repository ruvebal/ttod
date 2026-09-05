import typography from '@tailwindcss/typography';

/** Shared visual tokens for Tailwind-enabled islands in later phases. */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx}'],
  theme: {
    extend: {
      colors: { ink: '#211c15', paper: '#fbf8f1', surface: '#f1eadb', tao: '#8a651d' },
      fontFamily: { body: ['ui-serif', 'Georgia', 'serif'], ui: ['ui-sans-serif', 'system-ui', 'sans-serif'] },
    },
  },
  plugins: [typography],
};
