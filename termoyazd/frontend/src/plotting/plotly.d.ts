declare module 'plotly.js-basic-dist-min' {
  const plotly: {
    react: (element: HTMLElement, data: unknown[], layout: object, config: object) => Promise<void>;
    purge: (element: HTMLElement) => void;
    relayout: (element: HTMLElement, update: object) => Promise<void>;
    downloadImage: (element: HTMLElement, options: object) => Promise<unknown>;
    Plots: { resize: (element: HTMLElement) => Promise<void> };
  };
  export default plotly;
}
