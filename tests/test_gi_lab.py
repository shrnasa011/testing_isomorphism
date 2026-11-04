import unittest

from gi_lab.algorithms import ColorRefinement, StationaryDistribution, TwoWL
from gi_lab.exact import is_isomorphic
from gi_lab.families import cycle, disjoint_cycles, permuted, rook_graph, shrikhande_graph
from gi_lab.graph import Graph
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

    def test_stationary_distribution_is_relabeling_invariant(self):
        graph = rook_graph()
        algorithm = StationaryDistribution()
        self.assertEqual(algorithm.refine(graph).signature,
                         algorithm.refine(permuted(graph)).signature)

    def test_stationary_distribution_is_not_a_complete_isomorphism_test(self):
        # Both connected, 6-regular graphs have uniform stationary mass, but
        # the exact oracle confirms that they are not isomorphic.
        rook, shrikhande = rook_graph(), shrikhande_graph()
        algorithm = StationaryDistribution()
        self.assertFalse(is_isomorphic(rook, shrikhande))
        self.assertEqual(algorithm.refine(rook).signature,
                         algorithm.refine(shrikhande).signature)

    def test_stationary_distribution_separates_different_degree_distributions(self):
        # Both graphs are connected and have four vertices, but their degree
        # multisets differ: path P4 has (1, 1, 2, 2), while star K1,3 has
        # (1, 1, 1, 3). The stationary signatures therefore differ.
        path = Graph.from_edges([(0, 1), (1, 2), (2, 3)])
        star = Graph.from_edges([(0, 1), (0, 2), (0, 3)])
        algorithm = StationaryDistribution()
        self.assertFalse(is_isomorphic(path, star))
        self.assertNotEqual(algorithm.refine(path).signature,
                            algorithm.refine(star).signature)

    def test_stationary_collision_corpus_example_is_connected(self):
        # A focused regression: the test regards matching distributions as a
        # candidate match, although exact isomorphism says these differ.
        rook, shrikhande = rook_graph(), shrikhande_graph()
        algorithm = StationaryDistribution()
        left = algorithm.refine(rook)
        right = algorithm.refine(shrikhande)
        self.assertEqual(left.signature, right.signature)
        self.assertEqual(left.signature[1], ((6, 1 / 16),) * 16)
        self.assertFalse(is_isomorphic(rook, shrikhande))

    def test_stationary_distribution_accepts_disconnected_graphs(self):
        algorithm = StationaryDistribution()
        split = disjoint_cycles(6, 6)
        self.assertEqual(algorithm.refine(split).signature[1], ((2, 1 / 12),) * 12)

        with_isolate = Graph.from_edges([(0, 1)], vertices=range(3))
        self.assertEqual(algorithm.refine(with_isolate).signature[1],
                         ((0, 0), (1, 0.5), (1, 0.5)))

    def test_stationary_distribution_defines_edgeless_graphs(self):
        algorithm = StationaryDistribution()
        isolates = Graph.from_edges([], vertices=range(4))
        self.assertEqual(algorithm.refine(isolates).signature[1], ((0, 0.25),) * 4)
        empty = Graph.from_edges([])
        self.assertEqual(algorithm.refine(empty).signature, (0, ()))

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

    def test_erdos_search_accepts_expected_average_degree(self):
        algorithm = StationaryDistribution()
        by_probability = find_collision(
            algorithm, vertices=10, model="erdos", probability=0.5,
            samples=10, seed=19,
        )
        by_average_degree = find_collision(
            algorithm, vertices=10, model="erdos", average_degree=4.5,
            samples=10, seed=19,
        )
        self.assertEqual(by_average_degree, by_probability)

    def test_erdos_average_degree_validation(self):
        algorithm = StationaryDistribution()
        with self.assertRaisesRegex(ValueError, "vertices - 1"):
            find_collision(algorithm, vertices=5, model="erdos", average_degree=5,
                           samples=1, seed=0)
        with self.assertRaisesRegex(ValueError, "only available"):
            find_collision(algorithm, vertices=5, model="regular", average_degree=2,
                           samples=1, seed=0)


if __name__ == "__main__":
    unittest.main()
