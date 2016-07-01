import platform

_architecture = platform.machine()
if _architecture == 'alpha':
    from IN_alpha import *
elif _architecture.startswith('parisc'):
    from IN_hppa import *
elif _architecture.startswith('mips'):
    from IN_mips import *
elif _architecture.startswith('sparc'):
    from IN_sparc import *
else:
    from IN_default import *
