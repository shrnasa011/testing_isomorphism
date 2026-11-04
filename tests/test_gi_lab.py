import unittest

from gi_lab.algorithms import ColorRefinement, TwoWL
from gi_lab.exact import is_isomorphic
from gi_lab.families import cycle, disjoint_cycles, permuted, rook_graph, shrikhande_graph
from gi_lab.search import find_collision


class WorkbenchTests(unittest.TestCase):
    def test_relabelling_preserves_invariants_and_exact_truth(self):
        graph = rook_graph()
        renamed = permuted(graph)
        self.assertTrue(is_isomorphic(graph, renamed))
        for algorithm in (ColorRefinement(), TwoWL()):
            self.assertEqual(algorithm.refine(graph).signature, algorithm.refine(renamed).signature)

    def test_shrikhande_and_rook_are_a_known_1wl_collision(self):
        rook, shrikhande = rook_graph(), shrikhande_graph()
        self.assertFalse(is_isomorphic(rook, shrikhande))
        self.assertEqual(ColorRefinement().refine(rook).signature,
                         ColorRefinement().refine(shrikhande).signature)

    def test_1wl_is_blind_to_a_regular_component_split(self):
        connected, disconnected = cycle(12), disjoint_cycles(6, 6)
        self.assertFalse(is_isomorphic(connected, disconnected))
        self.assertEqual(ColorRefinement().refine(connected).signature,
                         ColorRefinement().refine(disconnected).signature)

    def test_simple_distinct_graphs_are_separated(self):
        self.assertNotEqual(ColorRefinement().refine(cycle(6)).signature,
                            ColorRefinement().refine(rook_graph()).signature)

    def test_seeded_regular_search_finds_a_reproducible_1wl_collision(self):
        collision = find_collision(ColorRefinement(), vertices=10, degree=2, samples=40, seed=7)
        self.assertIsNotNone(collision)
        assert collision is not None
        self.assertFalse(is_isomorphic(collision.left, collision.right))
        self.assertEqual(ColorRefinement().refine(collision.left).signature,
                         ColorRefinement().refine(collision.right).signature)

    def test_collision_search_can_require_connected_graphs(self):
        # 2-regular graphs on six vertices collide when the sample includes a
        # component split, but all connected examples are isomorphic C6s.
        self.assertIsNotNone(find_collision(
            ColorRefinement(), vertices=6, degree=2, samples=100, seed=7,
        ))
        self.assertIsNone(find_collision(
            ColorRefinement(), vertices=6, degree=2, samples=100, seed=7,
            connected_only=True,
        ))



if __name__ == "__main__":
    unittest.main()
