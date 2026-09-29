#include <16F886.h>
#fuses HS, NOWDT, NOLVP
#use delay(clock = 20000000)
unsigned int8 x = 0;

#INT_TIMER1
void timer_isr(void)
{
    set_timer1(3036); // nạp lại đầu tiên
    x = ~x;
    output_C(x);
}

void main()
{
    setup_timer_1(T1_INTERNAL | T1_DIV_BY_8);
    set_timer1(3036);
    output_C(x);
    enable_interrupts(INT_TIMER1);
    enable_interrupts(GLOBAL);
    while (TRUE) {
        // CPU rảnh: làm việc khác ở đây
    }
}