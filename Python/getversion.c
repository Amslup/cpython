
/* Return the full version string. */

#include "Python.h"

#include "patchlevel.h"

const char *
Py_GetVersion(void)
{
    static char version[250];
    PyOS_snprintf(version, sizeof(version), "%.80s (%.80s) %.80s",
                  PY_VERSION, Py_GetBuildInfo(), Py_GetCompiler());
    return version;
}

// Export the Python hex version as a constant.
const unsigned long Py_Version = PY_VERSION_HEX;
