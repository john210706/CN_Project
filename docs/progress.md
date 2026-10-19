# Implementation progress

- Read the full implementation brief; workspace initially empty.
- Host: Fedora 44; Python 3.14; no system compiler, CMake or NS-3.
- Installing isolated toolchain under .tools; upstream NS-3.45 under ignored vendor/.
- Design: C++ application-layer forwarding over actual ad-hoc Wi-Fi UDP broadcast;
  local HELLO measurements, serialized positions, finite processing queue, cancellable
  receiver timers. Initial fixed routes use offline geometry. No runtime global oracle.
- Build, runtime results, tests and known gaps will be recorded in evidence/validation.md.
