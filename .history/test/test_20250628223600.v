
    `define DEBUG 1
    `define WIDTH 32

    module test_module (
        input clk,
        input rst,
        output reg [WIDTH-1:0] count
    );

    `ifdef DEBUG
        initial $display("Debug mode enabled");
    `endif

    always @(posedge clk or posedge rst) begin
        if (rst) begin
            count <= 0;
        end else begin
            count <= count + 1;
        end
    end

    endmodule

