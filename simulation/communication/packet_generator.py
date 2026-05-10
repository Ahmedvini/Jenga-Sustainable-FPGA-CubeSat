"""Deterministic packet generator for tests and demos."""


def generate_packets(count: int) -> list[dict[str, int]]:
    return [{"id": 0x100 + index % 4, "payload": index} for index in range(count)]
