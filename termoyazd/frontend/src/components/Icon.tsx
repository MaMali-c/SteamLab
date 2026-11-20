export default function Icon({ name, size = 20 }: { name: string; size?: number }) {
  const paths: Record<string, string> = {
    calc: 'M5 3h14v18H5z M8 6h8v4H8z M8 14h1 M12 14h1 M16 14h1 M8 18h1 M12 18h1 M16 18h1',
    chart: 'M4 3v17h17 M7 15l4-6 4 3 5-8', layers: 'M3 7l9-5 9 5-9 5z M3 12l9 5 9-5 M3 17l9 5 9-5',
    book: 'M3 4h7l2 2 2-2h7v15h-7l-2 2-2-2H3z M12 6v15',
    temp: 'M10 14V5a2 2 0 0 1 4 0v9a5 5 0 1 1-4 0 M12 8v10',
    pressure: 'M4 18a9 9 0 1 1 16 0 M12 13l4-5 M9 18h6',
    box: 'M3 6l9-4 9 4v12l-9 4-9-4z M3 6l9 5 9-5 M12 11v11',
    energy: 'M13 2L5 14h6l-1 8 9-13h-6z', entropy: 'M2 14c3-12 7 12 10 0s7 12 10 0',
    drop: 'M12 2C9 8 4 11 4 16a8 8 0 0 0 16 0c0-5-5-8-8-14z',
    arrow: 'M5 12h14 M13 6l6 6-6 6', reset: 'M4 8a8 8 0 1 1-1 7 M4 3v5h5',
    check: 'M5 12l4 4L19 6', info: 'M12 11v6 M12 7h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
    help: 'M9 8a3 3 0 1 1 4 3c-1 1-1 1-1 3 M12 17h.01 M22 12a10 10 0 1 1-20 0 10 10 0 0 1 20 0',
    close: 'M6 6l12 12 M6 18L18 6', menu: 'M4 6h16 M4 12h16 M4 18h16',
    external: 'M14 3h7v7 M21 3l-11 11 M10 3H4v17h17v-6',
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={paths[name] ?? paths.info}/></svg>;
}
