let
	pkgs = (import <nixpkgs> {});
	python3WPkgs = pkgs.python3.withPackages (
			pkgs: with pkgs; [xdot amaranth matplotlib numpy]
	);
in pkgs.stdenv.mkDerivation {
	name = "fpga_workshop_demo";
	buildInputs = (with pkgs; [ graphviz readline zlib python3WPkgs gnuplot
							    gobject-introspection gtk3 yosys nextpnr verilog ]);
	passthru = {
		inherit (pkgs) readline zlib;
	};
}
