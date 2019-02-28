# Author: Jian Shi

import unittest
import numpy as np

from PySeismoSoil.class_site_factors import Site_Factors as SF
from PySeismoSoil.class_frequency_spectrum import Frequency_Spectrum as FS

class Test_Class_Site_Factors(unittest.TestCase):
    '''
    Unit test for Site_Factors class
    '''
    def test_range_check(self):
        self.assertEqual(SF._range_check(174, 300, 0.6), [1])
        self.assertEqual(SF._range_check(951, 300, 0.6), [1])
        self.assertEqual(SF._range_check(300, 7, 0.6), [2])
        self.assertEqual(SF._range_check(300, 901, 0.6), [2])
        self.assertEqual(SF._range_check(300, 600, 0.0009), [3])
        self.assertEqual(SF._range_check(300, 600, 1.501), [3])
        self.assertEqual(SF._range_check(300, 900, 0.5), [])
        self.assertEqual(SF._range_check(400, 900, 0.5), [])
        self.assertEqual(SF._range_check(450, 750, 0.5), [])
        self.assertEqual(SF._range_check(450, 751, 0.5), [4])
        self.assertEqual(SF._range_check(451, 750, 0.5), [4])
        self.assertEqual(SF._range_check(550, 600, 0.5), [])
        self.assertEqual(SF._range_check(551, 600, 0.5), [4])
        self.assertEqual(SF._range_check(550, 601, 0.5), [4])
        self.assertEqual(SF._range_check(600, 450, 0.5), [])
        self.assertEqual(SF._range_check(601, 450, 0.5), [4])
        self.assertEqual(SF._range_check(600, 451, 0.5), [4])
        self.assertEqual(SF._range_check(650, 300, 0.5), [])
        self.assertEqual(SF._range_check(651, 300, 0.5), [4])
        self.assertEqual(SF._range_check(650, 301, 0.5), [4])
        self.assertEqual(SF._range_check(750, 150, 0.5), [])
        self.assertEqual(SF._range_check(751, 150, 0.5), [4])
        self.assertEqual(SF._range_check(750, 151, 0.5), [4])
        self.assertEqual(SF._range_check(800, 75, 0.5), [])
        self.assertEqual(SF._range_check(801, 75, 0.5), [4])
        self.assertEqual(SF._range_check(800, 76, 0.5), [4])
        self.assertEqual(SF._range_check(850, 36, 0.5), [])
        self.assertEqual(SF._range_check(851, 36, 0.5), [4])
        self.assertEqual(SF._range_check(850, 37, 0.5), [4])

    def test_search_sorted(self):
        z1000_array = [8, 16, 24, 36, 75, 150, 300, 450, 600, 750, 900]

        loc = SF._search_sorted(24, z1000_array)
        self.assertEqual(loc, [1, 2])

        loc = SF._search_sorted(25, z1000_array)
        self.assertEqual(loc, [2, 3])

        loc = SF._search_sorted(60, z1000_array)
        self.assertEqual(loc, [3, 4])

        loc = SF._search_sorted(150, z1000_array)
        self.assertEqual(loc, [4, 5])

        loc = SF._search_sorted(8, z1000_array)
        self.assertEqual(loc, [0, 1])

        loc = SF._search_sorted(900, z1000_array)
        self.assertEqual(loc, [9, 10])

    def test_find_neighbors(self):
        Vs30, z1000, PGA = 190, 60, 0.85
        locations = SF._find_neighbors(Vs30, z1000, PGA)
        self.assertEqual(locations[0], [0, 1])
        self.assertEqual(locations[1], [3, 4])
        self.assertEqual(locations[2], [7, 8])

        Vs30, z1000, PGA = 175, 900, 0.05
        locations = SF._find_neighbors(Vs30, z1000, PGA)
        self.assertEqual(locations[0], [0, 1])
        self.assertEqual(locations[1], [9, 10])
        self.assertEqual(locations[2], [0, 1])

        Vs30, z1000, PGA = 950, 120, 0.01
        locations = SF._find_neighbors(Vs30, z1000, PGA)
        self.assertEqual(locations[0], [15, 16])
        self.assertEqual(locations[1], [4, 5])
        self.assertEqual(locations[2], [0, 1])

    def test_interpolate(self):
        import itertools
        from scipy.interpolate import RegularGridInterpolator

        def f(x,y,z):
            return x + y + z

        x = [1, 2]
        y = [10, 20]
        z = [100, 200]

        vertices = list(itertools.product(x, y, z))
        point = (1.5, 15, 150)  # point at which you want to know the value

        data = f(*np.meshgrid(x, y, z, indexing='ij', sparse=False))
        my_interpolating_function = RegularGridInterpolator((x, y, z), data)

        benchmark = my_interpolating_function(point)

        values_at_vertices = []
        for vertex in vertices:
            values_at_vertices.append([f(*vertex)])

        answer = SF._interpolate(vertices, values_at_vertices, point)

        self.assertEqual(answer, benchmark)

    def test_site_factors(self):
        sf = SF(265, 128, 0.012)

        # assert data type
        amp = sf.get_amplification(Fourier=False, show_interp_plots=False)
        self.assertTrue(isinstance(amp, FS))

        # assert that linear amplification factor starts from ~1.0 at small freq
        amp = sf.get_amplification(Fourier=True, show_interp_plots=False)
        self.assertTrue(isinstance(amp, FS))
        self.assertTrue(np.allclose(amp.raw_data[0, 1], 1.0, atol=0.07))

        # assert that phase start from ~0.0 at small freq
        phase = sf.get_phase_shift(show_interp_plots=False, method='eq_hh')
        self.assertTrue(isinstance(phase, FS))
        self.assertTrue(np.allclose(phase.raw_data[0, 1], 0.0, atol=0.07))


def test_interp_plots(vs30, z1000, pga):
    '''
    This isn't part of the unit test, because it plots figures. Just a visual
    check that the results look OK.

    Do not indent this function.
    '''
    sf = SF(vs30, z1000, pga)
    sf.get_amplification(Fourier=False, show_interp_plots=True)
    sf.get_amplification(Fourier=True, show_interp_plots=True)
    sf.get_phase_shift(show_interp_plots=True)

if __name__ == '__main__':
    SUITE = unittest.TestLoader().loadTestsFromTestCase(Test_Class_Site_Factors)
    unittest.TextTestRunner(verbosity=2).run(SUITE)

    test_interp_plots(365, 247, 0.75)