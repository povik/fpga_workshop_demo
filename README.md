# Demonstration design for an FPGA workshop

This project is a demonstration of some topics in FPGA programming, originally prepared for an FPGA workshop. The project is a very basic logic design for the Lattice ICE40UP5K part. It is tasked with driving an external LED in the pattern of a sinusoidal waveform (smoothly dimming and brightening the LED).

The project demonstrates a few things:

 * A fully open-source flow for the compilation of FPGA designs up to a result that can be programmed onto the chip (synthesis by [Yosys/ABC](https://github.com/YosysHQ/yosys); place and route by [nextpnr](https://github.com/YosysHQ/nextpnr))

 * A combination of traditional HDL languages (Verilog) and modern Python DSLs ([Amaranth](https://amaranth-lang.org/docs/amaranth/latest/intro.html)) *in a single design*. (Here the [Python DSL part](modules/sinusgen/design.py) generates the sinusoidal pattern, the [remainder](modules/top.v) does the pulse-density modulation.)

 * Simulation at either the [Python DSL level](modules/sinusgen/sim.py), or an end-to-end simulation at the [level of the completed mixed-language design](simulation/bench.v)

Please see the [Makefile](Makefile) to read the steps in the implementation of the above.

## Software dependencies

These are roughly the commands to install all the software dependencies on a recent Ubuntu release:

	apt install yosys nextpnr-ice40 iverilog fpga-icestorm gtkwave graphviz gnuplot
	pip3 install amaranth amaranth-yosys xdot

Alternatively, see [shell.nix](shell.nix) for a declaration of a NixOS development environment containing all the dependencies.
