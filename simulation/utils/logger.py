"""Tiny logger wrapper used by scripts."""


def info(message: str) -> None:
    print(f"[EcoSat] {message}")
