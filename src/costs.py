"""Execution-cost registry. Each level records where it came from, so a reader can see
the provenance rather than infer it.

UNIT CONVENTION, used consistently throughout:
    cost is always per leg, applied to turnover = |change in position|.
    Positions are in {-1, 0, +1}, so a complete round trip is two legs.
        round-trip cost = 2 * per-leg cost
    A direct reversal from +1 to -1 produces turnover of 2 in one step, and is therefore
    also two legs.
"""

MODELS = {
 'live': dict(
    leg=0.175, label='Measured execution benchmark',
    src='Calibrated from realised execution on this contract, August 2026.',
    covers='All-in: commission, spread and latency.',
    note='An enforced benchmark rather than an average: execution is monitored and gated '
         'when cost exceeds this level, so the realised cost distribution is bounded above. '
         'Applying 0.175 flat is therefore conservative.'),

 'gz': dict(
    leg=0.2965, label='Unconditional liquidity taker',
    src='Author\'s microstructure calibration on this contract, June 2026.',
    covers='Effective spread ~0.41 plus commission 0.175, both per round trip.',
    note='Roll (1984) on de-duplicated transaction prices, cross-checked against '
         'Corwin-Schultz (0.66). This is the charge for a participant who crosses the spread '
         'on every order and does not manage execution. Retained as the pessimistic reference.'),

 'stress': dict(
    leg=0.40, label='Degraded execution',
    src='Derived: the measured benchmark plus one tick of slippage per leg, rounded up.',
    covers='Execution failure: a broken gate or thin liquidity.',
    note='Used to ask how far the edge survives, never used for a reported figure.'),

 'zero': dict(
    leg=0.0, label='Zero cost (diagnostic)',
    src='—',
    covers='Gross only, separating the edge from friction.',
    note='Never the basis of a verdict.'),
}

DEFAULT = 'live'

def leg(name=DEFAULT):
    """Cost per leg."""
    return MODELS[name]['leg']

def rt(name=DEFAULT):
    """Cost per round trip: twice the per-leg cost."""
    return 2.0 * MODELS[name]['leg']

def explain(name=DEFAULT):
    m = MODELS[name]
    return (f"{m['label']}: {m['leg']:.4f} per leg = {2*m['leg']:.3f} per round trip\n"
            f"  source : {m['src']}\n"
            f"  covers : {m['covers']}\n"
            f"  note   : {m['note']}")

if __name__ == '__main__':
    for k in MODELS:
        print(f"[{k}]  {explain(k)}\n")
