import argparse
import logging

from .builder_registries import builder_registry


def build():
    raise ValueError()


def parse_arguments(text):
    parser = argparse.ArgumentParser()
    builder.add_argument("--source", help="The folder to look within")
