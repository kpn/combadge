from sys import version_info

SLOTS = {"slots": True} if version_info >= (3, 10) else {}
