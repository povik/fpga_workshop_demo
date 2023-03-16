module bench;
    reg clk = 0;
    always #5 clk = !clk;

    wire led0, led1;
    top top(clk, led0, led1);

    initial begin
        $dumpfile("waves.vcd");
        $dumpvars(0, bench);

        # 100000000 $finish;
    end
endmodule
