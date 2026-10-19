### What is being simulated?
Actual NS-3 ad-hoc Wi-Fi radios carry UDP broadcasts. A line in playback is drawn only
when a receiver event exists. The positions come from NS-3's mobility models.

### Three forwarding rules
**Fixed:** only an initially designated next hop forwards. **Opportunistic:** receivers
compete using measured incoming link reception and progress toward the target.
**Deadline-aware:** receivers also account for queue workload and predicted slack,
reject predicted misses, and cancel pending packets at expiry.

### How to read the evidence
PDR measures unique delivered packets; DSDR measures unique on-time deliveries divided
by all generated packets. Delay covers delivered packets only. Candidate scores and
remaining-delay estimates are predictions; destination timestamps are observations.
A suppression event requires a real overheard forward. Hidden terminals can produce
duplicates. Protocol comparisons require matching batch scenarios, not merely matching
packet IDs across unrelated stochastic runs.

### Main assumptions
Target coordinates are initially configured. Progress is greedy. Delay prediction is
approximate. The fixed baseline uses the same broadcast transport and is not AODV.
A deadline-aware policy can lose useful opportunities when its estimate is inaccurate.
This tool does not guarantee real-world emergency delivery.
