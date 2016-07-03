#include <X11/Xlib.h>
#include <stdio.h>

const static char PROP_NAME[] = "_NET_DESKTOP_VIEWPORT";

static Display* DUMMY_DISPLAY = NULL;

void get_root_cardinal(int* x_pos, int* y_pos){
    Window window;

    int result;
    Atom property;
    Atom actual_type_return;
    int actual_format_return;
    unsigned long bytes_after_return;
    unsigned char* prop_return;
    unsigned long n_items;

    if (! DUMMY_DISPLAY) {
        DUMMY_DISPLAY= XOpenDisplay(NULL);
    }

    window = RootWindow(DUMMY_DISPLAY, XDefaultScreen(DUMMY_DISPLAY));

    *x_pos = 0;
    *y_pos = 0;

    property = XInternAtom(DUMMY_DISPLAY, PROP_NAME, True);

    result = XGetWindowProperty(
                DUMMY_DISPLAY,
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
