import numpy as np
import amaranth as nm
from amaranth.hdl.rec import Record

class SinusGen(nm.Elaboratable):
    '''
    Sinus generator module

    Given a phase input `phi`, the module generates `cos` and `sin` outputs
    corresponding to cos(phi) and sin(phi).

    Parameters `phasebits` and `valbits` specify input and ouput bitwidth
    respectively.

    `phi` input is unsigned, and it's full range is mapped to [0, 2*pi).

    `cos` and `sin` outpus are signed, their maximum symmetric span is
    mapped to [-1, 1].
    '''
    def __init__(self, phasebits=8, valbits=8):
        self.phase = nm.Signal(nm.unsigned(phasebits))
        self.cos = nm.Signal(nm.signed(valbits))
        self.sin = nm.Signal(nm.signed(valbits))

    def build_lut(self, m, octant_phase):
        '''
        Build a lookup table (LUT) of the sin/cos values in the first
        phase octant [0, pi/4].
        '''

        # Create a structured signal composed of `cos` and `sin` fields
        # each `valbits` wide.
        valbits = len(self.sin)
        lut_value = Record([("cos", nm.signed(valbits)), ("sin", nm.signed(valbits))])

        # Add read-only memories for looking up the sine and cosine value
        scale = ((1 << (valbits - 1)) - 1)
        for func, datasig in zip([np.cos, np.sin], [lut_value.cos, lut_value.sin]):
            depth = (1 << (len(octant_phase) - 1)) + 1
            mem = nm.Memory(width=valbits, depth=depth, init=(i := [
                int(np.round(func(ph) * scale))
                for ph in (np.linspace(0.0, np.pi / 4, depth, endpoint=True))
            ]))
            rdport = mem.read_port()
            m.submodules += [rdport]
            m.d.comb += [
                rdport.addr.eq(octant_phase),
                datasig.eq(rdport.data),
            ]

        return lut_value.cos, lut_value.sin

    def elaborate(self, platform):
        m = nm.Module()

        top_phase = nm.Signal(nm.unsigned(3))
        top_phase_delay1 = nm.Signal(nm.unsigned(3))
        bot_phase = nm.Signal(nm.unsigned(len(self.phase) - 3))
        self.octant_phase = octant_phase = nm.Signal(nm.unsigned(len(bot_phase) + 1))

        cos_, sin_ = self.build_lut(m, octant_phase)

        m.d.sync += [
            top_phase_delay1.eq(top_phase),
        ]

        m.d.comb += [       
            # decompose phase into top 3 bits (top_phase) and the remainder (bot_phase)
            nm.Cat([bot_phase, top_phase]).eq(self.phase),
            # select a related phase from the [0, pi/4) range (octant_phase) that we will
            # be looking up 
            octant_phase.eq(nm.Mux(~top_phase[0], bot_phase,
                                   ((1 << len(bot_phase)) - bot_phase))),
            # use the looked-up values to derive the final cos/sin output by flipping
            # signs and swapping the cos/sin components as appropriate
            self.cos.eq(nm.Array([
                cos_,
                sin_,
                -sin_,
                -cos_,
                -cos_,
                -sin_,
                sin_,
                cos_,
            ])[top_phase_delay1]),
            self.sin.eq(nm.Array([
                sin_,
                cos_,
                cos_,
                sin_,
                -sin_,
                -cos_,
                -cos_,
                -sin_,
            ])[top_phase_delay1]),
        ]

        return m

if __name__ == "__main__":
    top = SinusGen()
    kwargs = {
        "ports": [top.phase, top.sin, top.cos],
        "name": "sinusgen"
    }

    import argparse
    from amaranth.back import rtlil, verilog
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out-rtlil', type=str,
                        help='output RTLIL', metavar='RTLIL_FILE')
    parser.add_argument('--out-verilog', type=str,
                        help='output Verilog', metavar='VERILOG_FILE')
    args = parser.parse_args()
    
    if args.out_rtlil:
        rtlil_source = rtlil.convert(top, **kwargs)
        with open(args.out_rtlil, "w") as f:
            f.write(rtlil_source)

    if args.out_verilog:
        verilog_source = verilog.convert(top, **kwargs)
        with open(args.out_verilog, "w") as f:
            f.write(verilog_source)
