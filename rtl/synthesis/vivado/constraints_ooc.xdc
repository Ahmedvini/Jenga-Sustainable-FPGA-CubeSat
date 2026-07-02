# Out-of-context constraints: 100 MHz reference clock for the accelerator.
# No physical pin assignments — this project characterizes the logic, it
# does not target a specific board's IO.
create_clock -period 10.000 -name clk [get_ports clk]
