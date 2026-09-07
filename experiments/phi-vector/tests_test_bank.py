"""Bank tests without the model: deposit cascade, lazy decay, floor, eviction, roundtrip."""
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from bank import PhiBank, TAUS, FLOOR, DEPOSIT, LOUDNESS, CAPS

def test():
    b = PhiBank(d=8, max_bytes=10_000)
    assert b.max_traces == 277

    # deposit cascade: user/record/t3
    amps = b.deposit_amplitudes("user", "record", "t3")
    assert all(abs(a-e) < 1e-9 for a, e in zip(amps, [1.0, 0.8, 0.8, 0.25, 0.1])), amps
    # cap clips components to 1.0; asserted layer emphasis may reach cap*1.6
    amps = b.deposit_amplitudes("user", "anchor", "t1")
    assert all(abs(a-e) < 1e-9 for a,e in zip(amps,[1.6,1.0,0.75,0.375,0.15])), amps
    # own_derivation cap 0.6
    amps = b.deposit_amplitudes("own_derivation", "record", "t2")
    assert max(amps) <= 0.6 * 1.6, amps

    # two traces
    id1 = b.append(np.ones(8, dtype=np.float16), "user", "anchor", "t1", {"content": "cat Barsik"})
    id2 = b.append(np.full(8, 2, dtype=np.float16), "user", "record", "t3", {"content": "meeting"})
    assert (id1, id2) == (1, 2)

    # lazy decay: totals shrink with ticks
    b.tick = 0;  t0 = dict(b.loudest(10))
    b.tick = 20; t20 = dict(b.loudest(10))
    assert t20[1] < t0[1] and t20[2] < t0[2]

    # repeat re-amplifies
    before = dict(b.loudest(10))[2]
    b.touch(2)
    after = dict(b.loudest(10))[2]
    assert after > before

    # floor death: deposit is across all five (O-10), a trace dies when ALL
    # components fall below floor. record/t3 trace: t5 amp 0.1 crosses 0.01 at ~23026 ticks
    b.tick = 10_000
    assert 2 in dict(b.loudest(10))
    b.tick = 28_000  # both traces' slowest component below floor
    assert 1 not in dict(b.loudest(10)) and 2 not in dict(b.loudest(10))

    # prefix vectors shape + scaling
    b.tick = 0
    pv = b.prefix_vectors(5)
    assert pv is not None and pv.shape[0] == 2 and pv.shape[1] == 8

    # eviction: size bounded, quietest dropped
    b2 = PhiBank(d=8, max_bytes=10_000)
    for i in range(300):
        b2.append(np.full(8, i % 7, dtype=np.float16), "user", "note", "t3", {"content": f"x{i}"})
    assert len(b2.meta) <= b2.max_traces

    # export / import roundtrip
    with tempfile.TemporaryDirectory() as td:
        b.export(td)
        b3 = PhiBank(d=8)
        n = b3.import_(td)
        assert n == len(b.meta) and b3.tick == b.tick
        assert np.allclose(b3.amps, b.amps)
        assert np.allclose(b3.vecs.astype(np.float32), b.vecs.astype(np.float32))

    print("ALL BANK TESTS PASSED")

if __name__ == "__main__":
    test()
