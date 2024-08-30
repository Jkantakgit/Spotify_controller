#include <windows.h>

int main(void)
{
    char zPath[] = "C:\\Users\\PetrH\\Desktop\\Python\\Python_bot\\python_bot.py";
    ShellExecute(
        HWND_DESKTOP, //Parent window
        "open",       //Operation to perform
        zPath,        //Path to program
        NULL,         //Parameters
        NULL,         //Default directory
        SW_SHOW);     //How to open

    char szPath[] = "C:\\Users\\PetrH\\Desktop\\Python\\Apps\\main.pyw";
    ShellExecute(
        HWND_DESKTOP, //Parent window
        "open",       //Operation to perform
        szPath,       //Path to program
        NULL,         //Parameters
        NULL,         //Default directory
        SW_SHOW);     //How to open
}