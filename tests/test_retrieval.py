from types import SimpleNamespace
from app.services.retrieval import retrieve_candidates

def test_retrieval_filters_country_and_placement():
    request = SimpleNamespace(country="FR", device="mobile",
                              placement="homepage-banner", page_category="travel")
    result = retrieve_candidates(request)
    assert result
    assert all("FR" in c.countries for c in result)
    assert all("homepage-banner" in c.placements for c in result)
