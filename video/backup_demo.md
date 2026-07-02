# Backup Demo Video — Script and Shot List

Target length: **75 seconds** (guide allows 60–90 s). Screen capture at 1080p,
terminal font enlarged so commands are readable. Record only after the final
Phase 1 code is committed, so the video shows the submitted numbers.

## Shot list

| Time | On screen | Narration / caption |
| --- | --- | --- |
| 0:00–0:08 | Title card: "EcoSat — Sustainable Modular CubeSat Electronics" + repo URL | "EcoSat cuts CubeSat electronics energy use by duty-cycling modular subsystems across the orbit." |
| 0:08–0:30 | Terminal: `python3 simulation/main.py` — full run, ending on the printed summary lines | "One command regenerates every result. Baseline always-on electronics: 242.55 milliwatts. Our duty-cycled modular design: 126.54 — a 47.8 percent energy saving per orbit, verified by the test suite." |
| 0:30–0:45 | Open `results/graphs/power_vs_time.png` — baseline flat line vs. optimized sunlight/eclipse step profile | "Power over one 95-minute orbit: the baseline stays flat while EcoSat steps down to milliwatt levels during eclipse." |
| 0:45–1:00 | Terminal: `./rtl/simulations/iverilog/run_iverilog.sh` — three testbenches printing PASS | "The FPGA accelerator RTL — FIR filtering, telemetry compression, CAN filtering — passes self-checking Icarus Verilog testbenches." |
| 1:00–1:12 | Terminal: `./pmep_demo` — hot-swap enumeration and orbit power-mode trace | "And PMEP, our plug-and-play protocol, enumerates hot-swapped modules and switches their power modes live." |
| 1:12–1:15 | Closing card: "47.8% energy saved · ~92% battery-life extension · fully reproducible" | — |

## Recording checklist

- [ ] Fresh `git clone` into a clean folder; record from there (proves reproducibility).
- [ ] Terminal: dark theme, font ≥ 16 pt, window sized so no line wraps.
- [ ] Pre-compile `pmep_demo` off-camera so the demo command is just `./pmep_demo`.
- [ ] Do one silent rehearsal run to warm caches so commands return quickly on camera.
- [ ] Export as MP4 (H.264), ≤ 90 s, verify it plays on a second device.
- [ ] Add burned-in captions matching the narration (audio may be unavailable in the judging room).
