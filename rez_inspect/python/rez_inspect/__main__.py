import sys

from . import cli


namespace = cli.parse_arguments(sys.argv[1:])
cli.run(namespace)
