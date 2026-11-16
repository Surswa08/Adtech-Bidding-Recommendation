from types import SimpleNamespace
from app.services.bidding import expected_value_and_bid

def test_cpc_expected_value():
    campaign = SimpleNamespace(pricing_model="CPC", bid=2.0)
    value, bid = expected_value_and_bid(campaign, ctr=0.05, cvr=0.1)
    assert value == 0.1
    assert bid == 2.0

def test_cpa_expected_value():
    campaign = SimpleNamespace(pricing_model="CPA", bid=20.0)
    value, bid = expected_value_and_bid(campaign, ctr=0.05, cvr=0.1)
    assert value == 0.1
    assert bid == 20.0

def test_cpm_expected_value():
    campaign = SimpleNamespace(pricing_model="CPM", bid=8.0)
    value, bid = expected_value_and_bid(campaign, ctr=0.05, cvr=0.1)
    assert value == 0.008
    assert bid == 8.0
