# Offline acceptance example

`acceptance.py` summarizes synthetic records containing a boolean `ok` and a
nonnegative, finite numeric `duration_ms`. It returns the total count, success
count, success rate, and mean duration across all records. Empty input returns
zero counts and `0.0` for both rate and mean. Invalid records raise `ValueError`;
the input is not modified.

This example and its tests use synthetic data for offline functional acceptance
only. They make no network or API calls and do not demonstrate API performance,
deployment success, or an SLA. Delivery is for draft review only; publishing and
PR creation belong to the trusted publisher.

Run from the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```
