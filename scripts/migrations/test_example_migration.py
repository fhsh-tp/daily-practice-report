"""Example migration for testing purposes. Not a real migration."""


async def forward() -> None:
    """Example forward migration (no-op)."""
    pass


async def backward() -> None:
    """Example backward migration (no-op)."""
    pass
