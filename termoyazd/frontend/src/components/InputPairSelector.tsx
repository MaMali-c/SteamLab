import { PAIRS, PARAMETERS, type PairId } from '../model';
import Icon from './Icon';
export default function InputPairSelector({ selected, onSelect }: { selected: PairId; onSelect: (pair: PairId) => void }) {
  return <div className="pair-grid" role="group" aria-label="Select input pair (انتخاب جفت ورودی)">{PAIRS.map(pair => <button type="button" key={pair.id} className={`pair-option ${selected === pair.id ? 'selected' : ''}`} aria-pressed={selected === pair.id} onClick={() => onSelect(pair.id)} title={`${PARAMETERS[pair.parameters[0]].name} + ${PARAMETERS[pair.parameters[1]].name} (${PARAMETERS[pair.parameters[0]].fa} و ${PARAMETERS[pair.parameters[1]].fa})${!pair.available ? ' — رابط آماده؛ حلگر هنوز متصل نیست' : ''}`}><span className="pair-symbols">{pair.parameters[0]}<span>+</span>{pair.parameters[1]}</span><span className={`pair-availability ${pair.available ? 'ready' : ''}`}>{pair.available ? <><Icon name="check" size={11}/>Live</> : 'UI ready'}</span></button>)}</div>;
}
