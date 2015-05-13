#! /usr/bin/python

import unittest
import instcalc

class TestGridData(unittest.TestCase):
	def setUp(self):
		self.arrGridSimple = [[0,0,0,0],[1.,1.,1.,1.], [2,2,2,2]]
		self.arrGridComplex = [[0.000 ,0.000,523.48,520.71],[0.000,0.015,535.17,716.88],[0.000,0.030,525.07,906.22]]
		self.arrBoreSimple = [[0,1,0],[90,0,1],[180,-1,0],[270,0,-1]]
		self.arrBoreComplex = [[0.0,70.41,699.34],[30.0,226.18,897.68],[60.0,459.81,992.51], \
							[90.0,707.15,958.16],[-30.0,42.58,448.13],[-60.0,138.37,216.91],[-90.0,337.23,65.37]]

		self.instSimple = instcalc.GridData(self.arrGridSimple)
		self.instComplex = instcalc.GridData(self.arrGridComplex)
		self.boreSimple = instcalc.BoresightData(self.arrBoreSimple)
		self.boreComplex = instcalc.BoresightData(self.arrBoreComplex)

	"""def test_rotationAngleSimple(self):
		self.assertEqual(self.instSimple.rotationAngle(),0)"""

	def test_rotationAngleComplex(self):
		self.assertEqual(self.instComplex.rotationAngle(),0)

	"""def test_plateScaleSimple(self):
		starPos = [self.arrGridSimple[0][3],self.arrGridSimple[1][3]]
		telPos = [self.arrGridSimple[0][1],self.arrGridSimple[1][1]]
		self.assertEqual(self.instSimple.plateScale(telPos, starPos),.5)

	def test_plateScaleComplex(self):
		starPos = [[self.arrGridComplex[0][2],self.arrGridComplex[0][3]],[self.arrGridComplex[1][2],self.arrGridComplex[1][3]]]
		telPos = [[self.arrGridComplex[0][0],self.arrGridComplex[0][1]],[self.arrGridComplex[1][0],self.arrGridComplex[1][1]]]
		self.assertEqual(self.instComplex.plateScale(telPos, starPos),10400)

	def test_boresightPosSimple(self):
		self.assertEqual(self.boreSimple.findCenter(),(0,0))

	def test_boresightPosComplex(self):
		x,y = self.boreComplex.findCenter()
		self.assertEqual((int(x), int(y)),(518,513))"""


if __name__ == '__main__':
    unittest.main()
