RTL_SOURCES = modules/top.v build/sinusgen.il
SIM_SOURCES = simulation/bench.v modules/top.v build/sinusgen.v

all: build/impl_ice40.bin build/sim build/sinusgen.png

clean:
	rm build/*

# sinusgen: Conversion from Amaranth (Python)

build/sinusgen.il: modules/sinusgen/design.py
	python3 $^ --out-rtlil $@

build/sinusgen.v: modules/sinusgen/design.py
	python3 $^ --out-verilog $@

# Simulation at sinusgen level

build/sinusgen.log: modules/sinusgen/design.py modules/sinusgen/sim.py
	python3 modules/sinusgen/sim.py > build/sinusgen.log

build/sinusgen.png: build/sinusgen.log
	gnuplot -e 'set terminal png; plot "$^" using 1:2, "$^" using 1:3;' > $@

# Simulation at full design level (with Icarus Verilog)

build/sim: $(SIM_SOURCES)
	iverilog -DSIMULATION -o $@ $^

# ICE40 Synthesis & Implementation

build/synth_ice40.json: $(RTL_SOURCES)
	yosys -p 'synth_ice40 -top top -json build/synth_ice40.json' $^

build/impl_ice40.asc: build/synth_ice40.json constraints/ice40.pcf constraints/ice40.sdc
	nextpnr-ice40 --up5k --package sg48 --json build/synth_ice40.json \
				  --pcf constraints/ice40.pcf --asc build/impl_ice40.asc \
				  --pre-pack constraints/ice40.sdc

%.bin: %.asc
	icepack $^ $@
