export default function SectionHeading({ number, title, fa, note }: { number: string; title: string; fa: string; note?: string }) {
  return <div className="section-heading"><span className="step-number">{number}</span><h2>{title}<small lang="fa" dir="rtl">{fa}</small></h2>{note && <span className="section-note">{note}</span>}</div>;
}
