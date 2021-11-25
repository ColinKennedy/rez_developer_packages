"""Find all user-registered plug-ins, if they exist."""

from .commands.builder_registries import builder_registry

builder_registry.register_user_plugins()
