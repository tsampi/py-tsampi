import platform

_architecture = platform.machine()
if _architecture.startswith('mips'):
    from DLFCN_mips import *
else:
    from DLFCN_default import *
