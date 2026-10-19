# Implementation notes

`packet-header` owns serialization. `model.h` owns validated configuration and a pure
candidate-scoring function. `routing` owns per-node state, beacons, finite processing
reservations, timers and event logging. `main.cc` creates the actual Wi-Fi/IP topology,
independent random streams, initial fixed routes, traffic and radio traces. This split
keeps networking behavior in C++ and offline data processing in Python.

The source tree is linked into the upstream scratch directory through its own CMakeLists.
Only the required modules and their transitive dependencies are built. No upstream source
files are modified. The executable location is discovered and checked before launch.
Python passes argument arrays, never shell-interpolated user values. Every run receives
a fresh UUID directory. The C++ program independently refuses nonempty trace output paths.

The report generator reads successful batch metadata and metrics. The dashboard accepts
existing results even if the executable is absent. Malformed result schemas produce an
error message instead of substituting sample values. All final figures use measured data.
