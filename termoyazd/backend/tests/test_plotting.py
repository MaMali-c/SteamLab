import pytest
from fastapi.testclient import TestClient
from iapws import IAPWS97
from app.main import app
from app.plotting import saturation_data

def test_saturation_forward_equations_and_cache():
    data=saturation_data()
    assert saturation_data() is data
    assert len(data['points'])==161
    assert data['critical']['included'] is False
    assert data['points'][-1]['T']==pytest.approx(data['critical']['T']-.05)
    for sample in data['points'][::20]:
        liquid=IAPWS97(T=sample['T']+273.15,x=0)
        vapor=IAPWS97(T=sample['T']+273.15,x=1)
        assert sample['P']==pytest.approx(liquid.P*1000)
        for key,expected in {'sf':liquid.s,'sg':vapor.s,'hf':liquid.h,'hg':vapor.h,'vf':liquid.v,'vg':vapor.v}.items():
            assert sample[key]==pytest.approx(expected,rel=1e-10)
    assert all(a['T']<b['T'] and a['P']<b['P'] for a,b in zip(data['points'],data['points'][1:]))

def test_saturation_api():
    response=TestClient(app).get('/api/diagrams/saturation')
    assert response.status_code==200
    assert response.headers['cache-control']=='public, max-age=3600'
    assert response.json()['units']['P']=='kPa'
