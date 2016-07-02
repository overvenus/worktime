#include <X11/Xlib.h>
#include <stdio.h>

const static char PROP_NAME[] = "_NET_DESKTOP_VIEWPORT";

void get_root_cardinal(int* x_pos, int* y_pos){
    Display* display;
    Window window;

    int result;
    Atom property;
    Atom actual_type_return;
    int actual_format_return;
    unsigned long bytes_after_return;
    unsigned char* prop_return;
    unsigned long n_items;

    display = XOpenDisplay(NULL);
    window = RootWindow(display, XDefaultScreen(display));

    *x_pos = 0;
    *y_pos = 0;

    property = XInternAtom(display, PROP_NAME, True);

    result = XGetWindowProperty(
                display, 
                window,
                property,
                0,                  /* long_offset */
                10L,                /* long_length */
                False,              /* delete */
                AnyPropertyType,    /* req_type */
                &actual_type_return,
                &actual_format_return,
                &n_items,
                &bytes_after_return,
                &prop_return);
    if (result != Success){
        return;
    }

    *x_pos = ((int32_t *)prop_return)[0];
    *y_pos = ((int32_t *)prop_return)[2];

    if (prop_return) XFree((char *)prop_return);
}
