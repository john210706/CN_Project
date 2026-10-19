# Faculty demonstration (10–12 minutes)

1. State the research question: does choosing feasible receivers improve the fraction of
   packets delivered before expiry? A late warning can count as delivered yet be useless.
2. Show the architecture diagram. Point out the real NS-3 Wi-Fi MAC/PHY underneath UDP.
3. Run `make demo`, then `make dashboard`. Pick the two-node wireless run and inspect
   send/receive times. Explain socket submission versus actual PHY start.
4. Open broadcast/suppression runs. Select one packet; step through A's broadcast,
   both relay receptions, timers, one forward and the other relay's cancellation.
5. Open the deadline demo. Compare B's queue/processing prediction with C's feasible
   estimate. In the controlled `deadline` demo, packet 7 shows B with measured link quality 1.0
   and C with 0.9; basic forwarding uses B while deadline-aware uses C. This demo
   explicitly injects 10% receiver loss at C. Inspect the real candidate columns;
   do not infer winners from a score alone.
6. Open the expiration demo. Show zero data sends and a cancelled queued timer at expiry.
7. Open multihop. Trace increasing hop counts through the line network.
8. Open congestion and mobility. Show queue drops and actual moving MobilityModel positions.
9. Select a completed experiment batch. Compare DSDR first, then PDR, delay and overhead.
   Explain that each dot is a seed and some intervals overlap or include no improvement.
10. Present limitations: location staleness, greedy voids, hidden terminals, prediction error,
    broadcast fixed baseline and short simulation duration. End with the measured result,
    not a claim that deadline awareness always wins.

Suggested slides: problem; three protocols; NS-3 architecture; normalized algorithm;
coordination trace; experiment design; DSDR findings; delay/overhead tradeoff; limitations.
Use exported SVG figures and cite the exact batch directory.
