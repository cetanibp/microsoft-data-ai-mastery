# FAB-004 steady-state benchmark summary

## Scope

The standard `STEADY` workload loaded four independent synthetic objects with 1,000,000 rows each on F256. Each `SEQ1` and `PAR4` run processed 4,000,000 rows. Three paired repetitions used alternating order to reduce systematic cache and order bias.

All six runs passed correctness with zero rejected and duplicate rows.

## Raw results

| Repetition | Order | SEQ1 elapsed | PAR4 elapsed | SEQ1 throughput | PAR4 throughput |
|---:|---|---:|---:|---:|---:|
| 1 | SEQ1 → PAR4 | 76.648708 s | 29.773362 s | 52,186.138 rows/s | 134,348.281 rows/s |
| 2 | PAR4 → SEQ1 | 61.598644 s | 28.611560 s | 64,936.494 rows/s | 139,803.631 rows/s |
| 3 | SEQ1 → PAR4 | 61.623769 s | 28.494197 s | 64,910.018 rows/s | 140,379.463 rows/s |

## Median comparison

| Metric | SEQ1 median | PAR4 median | PAR4 change |
|---|---:|---:|---:|
| Elapsed time | 61.623769 s | 28.611560 s | 53.570578% lower |
| Throughput | 64,910.018 rows/s | 139,803.631 rows/s | 115.380669% higher |
| Maximum worker queue | 53.030026 s | 18.498638 s | 65.116672% lower |
| Speed | — | — | 2.153807× |

## Provisional decision

`PAR4` passes the elapsed-time rule: the required improvement is at least 15%, and the observed median improvement is 53.57%.

The design decision remains provisional until Capacity Metrics evidence establishes CU seconds, normalized CU seconds per million rows, utilization, and throttling for the measured run windows. The first `SEQ1` observation was slower than the two warmed sequential runs, but the median limits its influence and both execution orders still favored `PAR4`.
