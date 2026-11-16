def choose_creative(campaign, request):
    # Deterministic compatibility preference; no runtime creative generation.
    creatives = campaign.creatives
    if not creatives:
        return None
    return sorted(creatives, key=lambda c: (
        c.get("format") == "image",
        c.get("width", 0) >= 300
    ), reverse=True)[0]

def rank_candidates(scored):
    return sorted(scored, key=lambda item: item["expected_value"], reverse=True)
