"""Run with an environment containing iapws/scipy; pytest not required."""
import sys,json,csv,math,unittest,platform
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'backend'))
from app.engine import solve,properties,PAIRS
from app.thermo import StateError
from app.plotting import saturation_data
from iapws import IAPWS97
import iapws,scipy

class EngineChecks(unittest.TestCase): pass

def roundtrip(pair):
 def check(self):
  seed=IAPWS97(P=.5,x=.4) if 'x' in pair else IAPWS97(T=573.15,P=.5)
  values=properties(seed)|{'x':.4};given={k:values[k] for k in pair.split('_')}
  try:r=solve(pair,given)
  except StateError as e:
   self.assertEqual(e.code,'ambiguous_state');self.assertTrue(any(abs(c['T']-values['T'])<1e-4 and abs(c['P']-values['P'])<1e-3 for c in e.candidates));return
  for k,err in r['convergence']['residuals'].items():self.assertLessEqual(abs(err),r['convergence']['tolerances'][k])
  self.assertAlmostEqual(r['full_state']['T'],values['T'],places=4)
  self.assertAlmostEqual(r['full_state']['P'],values['P'],places=3)
 return check
for pair in PAIRS:setattr(EngineChecks,'test_roundtrip_'+pair,roundtrip(pair))

def invalid(pair,values,code):
 def check(self):
  with self.assertRaises(StateError) as ctx:solve(pair,values)
  self.assertEqual(ctx.exception.code,code)
 return check
cases=[('T_x',{'T':100,'x':-1},'invalid_quality'),('T_x',{'T':100,'x':1.1},'invalid_quality'),('T_x',{'T':400,'x':.5},'quality_domain'),('P_x',{'P':23000,'x':.5},'quality_domain'),('T_P',{'T':900,'P':60000},'out_of_range'),('T_P',{'T':-1,'P':100},'out_of_range'),('T_P',{'T':300,'P':0},'out_of_range'),('P_v',{'P':100,'v':-1},'out_of_range'),('T_P',{'T':373.946,'P':22064},'critical_point'),('T_P',{'T':100,'P':IAPWS97(T=373.15,x=0).P*1000},'ambiguous_saturation'),('P_v',{'P':100,'v':IAPWS97(T=274.15,P=.1).v},'ambiguous_state')]
for i,args in enumerate(cases):setattr(EngineChecks,'test_invalid_or_ambiguous_'+str(i),invalid(*args))

def verification(self):
 for t,p,h,s,v in [(300,3,115.331273,.392294792,.00100215168),(700,.0035,3335.68375,10.1749996,92.3015898),(1500,.5,5219.76855,9.65408875,1.38455090)]:
  actual=solve('T_P',dict(T=t-273.15,P=p*1000))['full_state']
  for k,expected in dict(h=h,s=s,v=v).items():self.assertTrue(math.isclose(actual[k],expected,rel_tol=2e-8))
EngineChecks.test_official_verification=verification

def nearcritical(self):
 for t,p in [(376.85,25000),(373.8,22000)]:
  result=solve('T_P',dict(T=t,P=p));self.assertIsNone(result['quality']);self.assertTrue(all(math.isfinite(v) for v in result['full_state'].values()))
EngineChecks.test_nearcritical=nearcritical

def diagram(self):
 data=saturation_data();self.assertEqual(len(data['points']),161);self.assertIs(data,saturation_data());self.assertLess(data['points'][-1]['T'],data['critical']['T'])
EngineChecks.test_diagram=diagram

if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(EngineChecks))
 dataset=json.loads((root/'validation/reference_points.json').read_text());comparisons=[]
 for row in dataset['points']:
  actual=solve(row['pair'],row['inputs'])['full_state']
  for k,ref in row['reference'].items():
   delta=actual[k]-ref;half=row['rounding_half_step'][k]
   comparisons.append(dict(case=row['id'],table=row['table'],pdf_page=row['pdf_page'],property=k,reference=ref,calculated=actual[k],signed_error=delta,absolute_error=abs(delta),relative_error_percent=abs(delta)/abs(ref)*100,rounding_half_step=half,classification='within printed rounding' if abs(delta)<=half else 'exceeds rounding; formulation/source differences unresolved'))
 with (root/'validation/error_comparison.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=comparisons[0].keys());writer.writeheader();writer.writerows(comparisons)
 report={'python':platform.python_version(),'iapws':iapws.__version__,'scipy':scipy.__version__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'reference_states':len(dataset['points']),'comparisons':len(comparisons),'within_rounding':sum(r['classification']=='within printed rounding' for r in comparisons),'failure_details':[str(t)+'\n'+trace for t,trace in result.failures+result.errors]}
 (root/'validation/results.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
 sys.exit(not result.wasSuccessful())
