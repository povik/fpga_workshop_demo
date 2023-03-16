from design import SinusGen
from amaranth.sim import Simulator

dut = SinusGen(8, 8)

def bench():
    for ph in range(256):
        yield dut.phase.eq(ph)
        yield
        print(ph, (yield dut.cos), (yield dut.sin))

sim = Simulator(dut)
sim.add_clock(1e-6) # 1 MHz
sim.add_sync_process(bench)
sim.run()
