from lifex.life_sim import LifeSim
from lifex.engine_builder import create_engine
from lifex.rules import DEFAULT_RULE


def test_life_sim_step():
    s = LifeSim()
    s.configure({"rle_text": "bo$2bo$3o!"})
    s.setup()
    s.step()
    s.run(3)
    assert len(s.engine.alive_set()) > 0


def test_fallback_engine():
    e = create_engine("hashlife", DEFAULT_RULE)  # returns sparse if dep missing
    assert e is not None
