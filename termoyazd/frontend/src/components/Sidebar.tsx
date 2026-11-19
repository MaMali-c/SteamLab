import { useState } from 'react';
import Icon from './Icon';
const links = [
  { id: 'calculator', title: 'Property Calculator', fa: 'محاسبه خواص', icon: 'calc' },
  { id: 'diagrams', title: 'Thermodynamic Diagrams', fa: 'نمودارهای ترمودینامیکی', icon: 'chart' },
  { id: 'sources', title: 'About & Sources', fa: 'درباره پروژه و منابع', icon: 'book' },
  { id: 'help', title: 'Help', fa: 'راهنما', icon: 'help' },
];
export default function Sidebar({ online }: { online: boolean | null }) {
  const [active, setActive] = useState('calculator');
  const [open, setOpen] = useState(false);
  return <aside className={`sidebar ${open ? 'mobile-open' : ''}`}>
    <a className="brand" href="#calculator" onClick={() => setOpen(false)}><span className="brand-mark"><Icon name="drop" size={30}/></span><span>termoyazd<small>THERMODYNAMIC WORKSPACE</small></span></a>
    <button type="button" className="mobile-menu" aria-expanded={open} aria-controls="main-nav" aria-label="Toggle navigation (نمایش فهرست)" onClick={() => setOpen(!open)}><Icon name={open ? 'close' : 'menu'}/></button>
    <nav id="main-nav" aria-label="Main navigation"><p className="nav-caption">WORKSPACE <span>(محیط کار)</span></p>{links.map(link => <a key={link.id} href={`#${link.id}`} className={`nav-item ${active === link.id ? 'active' : ''}`} aria-current={active === link.id ? 'location' : undefined} onClick={() => { setActive(link.id); setOpen(false); }}><Icon name={link.icon}/><span>{link.title}<small lang="fa">{link.fa}</small></span>{active === link.id && <i/>}</a>)}</nav>
    <div className="fluid-card"><span className="fluid-icon"><Icon name="drop" size={23}/></span><div><strong>Water & steam</strong><small>آب و بخار خالص</small></div><span className="fluid-formula">H₂O</span></div>
    <div className="sidebar-footer"><span className={`connection ${online ? 'online' : ''}`}><i/>{online === null ? 'Loading scientific engine…' : online ? 'IF97 engine ready' : 'Engine unavailable'}</span><span>termoyazd <b>v0.1.0</b></span></div>
  </aside>;
}
