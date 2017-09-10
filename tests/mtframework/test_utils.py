import pytest

from albam.engines.mtframework.blender_export import _process_weights

VERTICES_WEIGHTS = (
    {0: [(1, 0.0021),
         (2, 0.50),
         (3, 0.0008),
         (4, 0.3687)
         ]
     },
    {0: [(1, 0.001),
         (2, 0.001),
         (3, 0.001),
         (4, 0.001)
         ]
     },
    {0: [(1, 0.999),
         (2, 0.001),
         (3, 0.001),
         (4, 0.001)
         ]
     },
    {0: [(1, 1.0),
         (2, 1.0),
         (3, 1.0),
         (4, 0.000001)
         ]
     },
)


@pytest.mark.parametrize('dict_input', VERTICES_WEIGHTS)
def test_bug(dict_input):

    out = _process_weights(dict_input)
    weights = [pairs[1] for pairs in out[0]]

    assert sum(weights) == 255
    assert all(map(lambda v: v > 0, weights))
