from app.data.catalog import CAMPAIGNS

def retrieve_candidates(request, max_candidates=100):
    candidates = []
    for campaign in CAMPAIGNS:
        if not campaign.active:
            continue
        if campaign.spent_today >= campaign.daily_budget:
            continue
        if request.country not in campaign.countries:
            continue
        if request.device not in campaign.devices:
            continue
        if request.placement not in campaign.placements:
            continue
        candidates.append(campaign)
    # Context match is a cheap retrieval preference, not a hard eligibility rule.
    candidates.sort(key=lambda c: c.category == request.page_category, reverse=True)
    return candidates[:max_candidates]
