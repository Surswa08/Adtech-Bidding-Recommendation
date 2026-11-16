from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("data")
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(42)
n = 30000
base_ctr = rng.uniform(0.01, 0.08, n)
base_cvr = rng.uniform(0.01, 0.20, n)
mobile = rng.integers(0, 2, n)
fr = rng.integers(0, 2, n)
context_match = rng.integers(0, 2, n)
user_clicks = rng.poisson(3, n)
user_impressions = rng.poisson(40, n)
logit_ctr = -3.8 + 12*base_ctr + .25*mobile + .35*fr + .75*context_match + .025*user_clicks
logit_cvr = -3.5 + 8*base_cvr + .10*mobile + .25*context_match + .01*user_clicks
sigmoid = lambda x: 1/(1+np.exp(-x))
ctr_p, cvr_p = sigmoid(logit_ctr), sigmoid(logit_cvr)
click = rng.binomial(1, ctr_p)
conversion = click * rng.binomial(1, cvr_p)
df = pd.DataFrame({
    "base_ctr":base_ctr, "base_cvr":base_cvr, "mobile":mobile, "fr":fr,
    "context_match":context_match, "user_clicks":user_clicks,
    "user_impressions":user_impressions, "click":click, "conversion":conversion
})
df.to_csv(OUT / "synthetic_training_data.csv", index=False)
print(f"Wrote {len(df)} synthetic rows to data/synthetic_training_data.csv")
