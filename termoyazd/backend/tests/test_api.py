import pytest
from fastapi.testclient import TestClient
from iapws import IAPWS97
from app.main import app
from app.engine import solve, properties, PAIRS
from app.thermo import StateError

client = TestClient(app)

@pytest.mark.parametrize('pair', PAIRS)
def test_all_pairs_roundtrip(pair):
    state = IAPWS97(P=0.5, x=0.4) if 'x' in pair else IAPWS97(T=573.15,P=0.5)
    data = properties(state) | {'x': 0.4}
    inputs = {key:data[key] for key in pair.split('_')}
    try:
        result = solve(pair, inputs)
    except StateError as error:
        assert error.code == 'ambiguous_state'
        assert len(error.candidates) > 1
        assert any(abs(c['T']-data['T']) < 1e-4 and abs(c['P']-data['P']) < 1e-3 for c in error.candidates)
        return
    assert len(result['calculated_properties']) == 4
    assert result['full_state']['T'] == pytest.approx(data['T'], abs=1e-4)
    assert result['full_state']['P'] == pytest.approx(data['P'], abs=1e-3)
    for key,residual in result['convergence']['residuals'].items():
        assert abs(residual) <= result['convergence']['tolerances'][key]

@pytest.mark.parametrize('t,p,h,s,v',[(300,3,115.331273,.392294792,.00100215168),(700,.0035,3335.68375,10.1749996,92.3015898),(1500,.5,5219.76855,9.65408875,1.38455090)])
def test_published_verification(t,p,h,s,v):
    result=solve('T_P',{'T':t-273.15,'P':p*1000})
    for key,value in dict(h=h,s=s,v=v).items():
        assert result['full_state'][key] == pytest.approx(value,rel=2e-8)
    assert result['quality'] is None

@pytest.mark.parametrize('pair,values', [('T_x',{'T':400,'x':.5}),('P_x',{'P':23000,'x':.5}),('T_x',{'T':100,'x':1.1}),('T_P',{'T':900,'P':60000}),('P_v',{'P':500,'v':-1})])
def test_invalid_states(pair,values):
    with pytest.raises(StateError): solve(pair,values)

def test_saturation_ambiguity():
    p=IAPWS97(T=373.15,x=0).P*1000
    with pytest.raises(StateError,match='saturation'): solve('T_P',{'T':100,'P':p})

@pytest.mark.parametrize('x',[0,.3,1])
def test_quality_endpoints_and_mixture(x):
    result=solve('P_x',{'P':500,'x':x})
    assert result['quality']==pytest.approx(x)
    state=result['full_state']
    assert state['h']-state['u']==pytest.approx(state['P']*state['v'],abs=1e-6)

def test_non_unique_cold_water_volume():
    # Water density maximum gives two temperatures at this pressure/volume.
    state=IAPWS97(T=274.15,P=.1)
    with pytest.raises(StateError) as error:
        solve('P_v',{'P':100,'v':state.v})
    assert error.value.code=='ambiguous_state'
    assert len(error.value.candidates)>=2

def test_api_schema():
    response=client.post('/api/calculate',json={'input_pair':'T_P','values':{'T':300,'P':1000}})
    assert response.status_code==200
    assert response.json()['convergence']['converged']
    for values in ({'T':True,'P':1000},{'T':'300','P':1000},{'T':300,'P':1000,'h':1}):
        assert client.post('/api/calculate',json={'input_pair':'T_P','values':values}).status_code==422
