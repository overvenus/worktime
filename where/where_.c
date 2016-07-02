#include <Python.h>
#include "where.h"

// Python 2
#ifdef Py_InitModule3
#define PY2
#endif

// Python 3
#ifdef PyModule_Create
#define PY3
#endif


/* Docstrings */
static char module_docstring[] =
    "This module provides an interface for query the cardinal of X.org's"
    " root viewprot";
static char cardinal_docstring[] = "Query the cardinal of X.org's root viewprot!";

/* Available functions */
static PyObject *where_cardinal(PyObject *self, PyObject *args);

/* Module specification */
static PyMethodDef where_methods[] = {
    {"cardinal", where_cardinal, METH_VARARGS, cardinal_docstring},
    {NULL, NULL, 0, NULL}
};

#ifdef PY3
static struct PyModuleDef where_module = {
        PyModuleDef_HEAD_INIT,
        "where_",   /* name of module */
        module_docstring, /* module documentation, may be NULL */
        -1,       /* size of per-interpreter state of the module,
                or -1 if the module keeps state in global variables. */
        where_methods
};
#endif

/* Initialize the module */
#ifdef PY2
PyMODINIT_FUNC initwhere_(void)
{
    Py_InitModule3("where_", where_methods, module_docstring);
}
#endif

#ifdef PY3
PyMODINIT_FUNC PyInit_where_(void) {
    PyObject *m;
    m = PyModule_Create(&where_module);
    return m;
}
#endif

static PyObject *where_cardinal(PyObject *self, PyObject *args)
{
    PyObject *ret;
    PyObject *py_x;
    PyObject *py_y;

    int x;
    int y;

    get_root_cardinal(&x, &y);
    py_x = Py_BuildValue("i", x);
    py_y = Py_BuildValue("i", y);

    ret = PyTuple_New(2);
    PyTuple_SetItem(ret, 0, py_x);
    PyTuple_SetItem(ret, 1, py_y);

    return ret;
}
