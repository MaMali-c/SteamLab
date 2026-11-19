import {render,screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {it,expect} from 'vitest';
import Sidebar from './Sidebar';
it('opens mobile navigation and closes it after selecting a section',async()=>{
 render(<Sidebar online={true}/>);
 const menu=screen.getByRole('button',{name:/Toggle navigation/});
 expect(menu).toHaveAttribute('aria-expanded','false');
 await userEvent.click(menu);
 expect(menu).toHaveAttribute('aria-expanded','true');
 await userEvent.click(screen.getByRole('link',{name:/Thermodynamic Diagrams/}));
 expect(menu).toHaveAttribute('aria-expanded','false');
 expect(screen.getByRole('link',{name:/Thermodynamic Diagrams/})).toHaveAttribute('aria-current','location');
});
