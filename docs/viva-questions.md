# Viva preparation

1. **What is NS-3?** A discrete-event network simulator with protocol and radio models.
2. **Is this a real network deployment?** No; packets traverse simulated Wi-Fi stacks.
3. **What advances time?** The simulator event scheduler, not the host clock.
4. **Why broadcast?** One radio transmission can be decoded by several potential relays.
5. **Does Wi-Fi broadcast guarantee reception?** No; it has no per-receiver MAC ACK or retry.
6. **What is fixed here?** Initial BFS next-hop choices; the baseline is not AODV.
7. **What makes forwarding opportunistic?** Receivers that actually heard a packet compete.
8. **Why not always pick the strongest link?** It can lead to excessive remaining delivery delay.
9. **How is a deadline encoded?** An absolute integer-nanosecond expiry in the transmitted header.
10. **How is remaining time calculated?** Expiry minus Simulator::Now().
11. **Can a scheduled valid packet expire?** Yes; an expiry event cancels it and the send checks again.
12. **Is arrival at the deadline on time?** Yes; accounting uses arrival ≤ expiry.
13. **What is PDR?** Unique delivered packets divided by generated packets.
14. **What is DSDR?** Unique on-time deliveries divided by generated packets.
15. **Why is mean delay insufficient?** Dropping slow packets can reduce the delivered-only mean.
16. **What estimates link quality?** Locally received HELLO sequences over a bounded window.
17. **Is estimated delay observed delay?** No; it combines local workload, holdoff and predicted hops.
18. **Why normalize scores?** Raw metres, probabilities and milliseconds cannot be meaningfully added.
19. **How do receivers coordinate?** Priority timers and cancellation after an actual overheard forward.
20. **What happens with hidden terminals?** Candidates may not hear one another; duplicates can remain.
21. **How are loops limited?** Positive geographic progress, packet history and hop limits.
22. **How does mobility affect packets?** MobilityModel positions feed the real propagation calculations.
23. **What causes loss?** Radio reception failures, overflow, infeasibility, voids or insufficient observation.
24. **Why independent seeds?** To measure stochastic variation instead of relying on one favorable run.
25. **Why not use FlowMonitor alone?** Broadcast relay traffic needs custom end-to-end identity accounting.
26. **How is throughput counted?** Unique delivered payload bytes over the full measured interval.
27. **What is a confidence interval here?** A Student-t interval across independent per-run metrics.
28. **Does the algorithm always improve DSDR?** No; prediction error and conservative rejection can hurt.
29. **What information is globally available?** Initial mission locations and baseline route construction;
    runtime opportunistic decisions have only local state and transmitted metadata.
30. **What improvement would you study next?** Better observed delay prediction and location updates,
    tested against the same fair baselines and with longer independent runs.
