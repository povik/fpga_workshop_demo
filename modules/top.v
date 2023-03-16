module pwm(input clk, input rst,
           input [8:0] duty, output out);
    reg [8:0] counter = 0;

    always @ (posedge clk)
    begin
        if (rst) begin
            counter <= 0;
        end else begin
            counter <= (counter < 256) ?
                       (counter + 1) : 0;
        end
    end

    assign out = counter < duty;
endmodule

module top(input clk24, output led0, output led1);
    reg [24:0] phase = 0;
    always @ (posedge clk24)
        phase <= phase + 1;

    wire signed [7:0] sin, cos;

    sinusgen sinusgen(.clk(clk24), .phase(phase[24:17]),
                      .sin(sin), .cos(cos), .rst(1'b0));

    reg [8:0] pwm0_duty, pwm1_duty;

    always @ (posedge clk24)
    begin
        pwm0_duty <= sin + 128;
        pwm1_duty <= cos + 128;
    end

    wire pwm0_out, pwm1_out;

    pwm pwm0(
        .clk(clk24),
        .rst(1'b0),
        .duty(pwm0_duty),
        .out(pwm0_out)
    );
    pwm pwm1(
        .clk(clk24),
        .rst(1'b0),
        .duty(pwm1_duty),
        .out(pwm1_out)
    );

`ifndef SIMULATION
    SB_RGBA_DRV #(
        .CURRENT_MODE("0b0"),
        .RGB1_CURRENT("0b000010"), // 4 mA
        .RGB2_CURRENT("0b000010") // 4 mA
    ) rgba_driver(
        .CURREN(1),
        .RGBLEDEN(1),
        .RGB1PWM(pwm0_out),
        .RGB2PWM(pwm1_out),
        .RGB1(led0),
        .RGB2(led1)
    );
`else
    assign led0 = pwm0_out;
    assign led1 = pwm1_out;
`endif
endmodule
