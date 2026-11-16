def expected_value_and_bid(campaign, ctr: float, cvr: float):
    if campaign.pricing_model == "CPC":
        value = ctr * campaign.bid
        bid_price = campaign.bid
    elif campaign.pricing_model == "CPA":
        value = ctr * cvr * campaign.bid
        bid_price = campaign.bid
    else:  # CPM
        value = campaign.bid / 1000.0
        bid_price = campaign.bid
    # Expected value is expressed per impression in currency units.
    return value, bid_price
