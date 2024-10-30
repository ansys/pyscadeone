import sys

from ansys.scadeone.core.svc.simdata.stpimporter import cmd_parse

ret = cmd_parse()
sys.exit(ret)
