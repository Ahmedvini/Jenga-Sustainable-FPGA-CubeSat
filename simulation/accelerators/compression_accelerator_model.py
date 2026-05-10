"""Telemetry compression accelerator model."""


def rle_compress(samples: list[int]) -> list[tuple[int, int]]:
    if not samples:
        return []
    output = []
    current = samples[0]
    count = 1
    for sample in samples[1:]:
        if sample == current:
            count += 1
        else:
            output.append((current, count))
            current = sample
            count = 1
    output.append((current, count))
    return output
