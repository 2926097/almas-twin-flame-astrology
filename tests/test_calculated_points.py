import copy
import json
from math import cos, radians, sin, sqrt
from pathlib import Path
import unittest

from almas_tfa.calculated_points import (
    EARTH_MOON_GM_DE440, MAX_JD_TT, MIN_JD_TT, axis_sample_longitude,
    mean_apogee, osculating_apogee, vertex_axis,
)

ROOT=Path(__file__).resolve().parents[1]


def lunar_state(apogee_deg=40, epoch=2451545., eccentricity=0.0549):
    angle=radians(apogee_deg+180); eps=radians(23.4392911)
    radius=360000.; speed=sqrt(EARTH_MOON_GM_DE440*(1+eccentricity)/radius)
    r_ecl=(radius*cos(angle),radius*sin(angle),0.)
    v_ecl=(-speed*sin(angle),speed*cos(angle),0.)
    rotation=[[1.,0.,0.],[0.,cos(eps),sin(eps)],[0.,-sin(eps),cos(eps)]]
    transform=lambda vector:[sum(rotation[j][i]*vector[j] for j in range(3)) for i in range(3)]
    return dict(epoch_jd_tt=epoch,position_icrf_km=transform(r_ecl),velocity_icrf_km_s=transform(v_ecl),
        rotation_icrf_to_true_ecliptic=rotation,mu_km3_s2=EARTH_MOON_GM_DE440,frame='ICRF_INERTIAL',
        coordinate_origin='GEOCENTRIC',position_units='KM',velocity_units='KM_PER_SECOND')


class CalculatedPointGeometryTests(unittest.TestCase):
    def test_67_recorded_independent_implementation_comparisons_reproduce(self):
        report=json.loads((ROOT/'validation/ssar/calculated-points-precision.receipt.json').read_text())
        self.assertEqual(report['status'],'PASS');self.assertEqual(report['comparison_count'],67)
        for record in report['records']:
            data=record['input']
            if record['point_id']=='VERTEX': actual=vertex_axis(data['armc_deg'],data['latitude_deg'],data['obliquity_deg'])['vertex']
            elif record['point_id']=='BLACK_MOON_MEAN': actual=mean_apogee(data['jd_tt'],data['nutation_longitude_deg'])
            else: actual=osculating_apogee(data['position_icrf_km'],data['velocity_icrf_km_s'],data['rotation_icrf_to_true_ecliptic'],data['mu_km3_s2'])['longitude']
            self.assertLessEqual(abs((actual-record['reference_deg']+180)%360-180),record['tolerance_deg'])
        self.assertFalse(report['interpretation_validated'])
        self.assertFalse(report['independent_ephemeris_accuracy_validated'])

    def test_vertex_western_orientation_both_hemispheres_equator_and_high_latitude(self):
        for latitude in (0,18,-18,41,-41,70,-70):
            for armc in (15,90,170,270,345):
                result=vertex_axis(armc,latitude,23.4392911)
                longitude=radians(result['vertex']);theta=radians(armc);eps=radians(23.4392911)
                east=-sin(theta)*cos(longitude)+cos(theta)*sin(longitude)*cos(eps)
                self.assertLess(east,0)
                self.assertAlmostEqual((result['anti_vertex']-result['vertex'])%360,180,places=10)

    def test_vertex_intersection_with_prime_vertical_not_equatorial_ascendant(self):
        armc,latitude,eps=30,41,23.4
        longitude=radians(vertex_axis(armc,latitude,eps)['vertex'])
        theta,phi,epsilon=map(radians,(armc,latitude,eps))
        north=(-sin(phi)*cos(theta),-sin(phi)*sin(theta),cos(phi))
        direction=(cos(longitude),sin(longitude)*cos(epsilon),sin(longitude)*sin(epsilon))
        self.assertAlmostEqual(sum(a*b for a,b in zip(north,direction)),0,places=12)

    def test_vertex_periodicity_and_exact_axis_opposition(self):
        a=vertex_axis(345,41,23.4)
        self.assertEqual(a,vertex_axis(-15,41,23.4))
        self.assertEqual(a,vertex_axis(705,41,23.4))
        self.assertEqual(a['axis_longitude'],a['vertex']%180)

    def test_vertex_equator_resolves_zero_or_180_without_unconditional_zero(self):
        self.assertAlmostEqual(vertex_axis(90,0,23.4)['vertex'],0)
        self.assertAlmostEqual(vertex_axis(270,0,23.4)['vertex'],180)

    def test_vertex_poles_coincident_planes_and_unoriented_intersection_block(self):
        for args in ((30,90,23.4),(30,-90,23.4),(90,23.4,23.4),(0,0,23.4),(180,0,23.4),(30,41,19)):
            with self.assertRaises(ValueError): vertex_axis(*args)

    def test_vertex_nonfinite_boolean_and_string_inputs_rejected(self):
        for value in (float('nan'),float('inf'),True,'30'):
            with self.assertRaises(ValueError):vertex_axis(value,41,23.4)

    def test_mean_apogee_j2000_fundamental_arguments_and_nutation(self):
        expected=(93.27209062+125.04455501-134.96340251+180)%360
        self.assertAlmostEqual(mean_apogee(2451545.,0),expected,places=10)
        self.assertAlmostEqual(mean_apogee(2451545.,0.002)-mean_apogee(2451545.,0),0.002,places=11)

    def test_mean_apogee_tt_domain_boundaries_and_circular_range(self):
        for jd in (MIN_JD_TT,2451545,MAX_JD_TT):
            self.assertTrue(0<=mean_apogee(jd,0)<360)
        for jd in (MIN_JD_TT-1,MAX_JD_TT+1):
            with self.assertRaises(ValueError):mean_apogee(jd,0)

    def test_mean_apogee_bad_epoch_nutation_and_nonfinite_rejected(self):
        for args in ((2451545,2),(True,0),(2451545,float('nan')),(float('inf'),0)):
            with self.assertRaises(ValueError):mean_apogee(*args)

    def test_osculating_apogee_known_ellipse_direction_not_perigee(self):
        for longitude in (0,40,179.5,359.5):
            s=lunar_state(longitude)
            result=osculating_apogee(s['position_icrf_km'],s['velocity_icrf_km_s'],s['rotation_icrf_to_true_ecliptic'])
            self.assertLess(abs((result['longitude']-longitude+180)%360-180),1e-10)
            self.assertAlmostEqual(result['eccentricity'],0.0549,places=12)

    def test_osculating_rotation_after_inertial_vector_has_known_solution(self):
        s=lunar_state(41)
        result=osculating_apogee(s['position_icrf_km'],s['velocity_icrf_km_s'],s['rotation_icrf_to_true_ecliptic'])
        identity=[[1,0,0],[0,1,0],[0,0,1]]
        unrotated=osculating_apogee(s['position_icrf_km'],s['velocity_icrf_km_s'],identity)
        self.assertAlmostEqual(result['longitude'],41,places=10)
        self.assertGreater(abs(result['longitude']-unrotated['longitude']),1)

    def test_osculating_circular_parabolic_and_hyperbolic_states_block(self):
        for eccentricity in (0,1,1.1):
            s=lunar_state(eccentricity=eccentricity)
            with self.assertRaises(ValueError):osculating_apogee(s['position_icrf_km'],s['velocity_icrf_km_s'],s['rotation_icrf_to_true_ecliptic'])

    def test_osculating_zero_state_radial_motion_and_nonpositive_mu_block(self):
        identity=[[1,0,0],[0,1,0],[0,0,1]]
        for r,v,mu in (([0,0,0],[1,0,0],1),([1,0,0],[0,0,0],1),([1,0,0],[2,0,0],1),([1,0,0],[0,1,0],0)):
            with self.assertRaises(ValueError):osculating_apogee(r,v,identity,mu)

    def test_osculating_dimensions_finiteness_nonrotations_and_reflections_block(self):
        s=lunar_state()
        for field,value in (('position_icrf_km',[1,2]),('velocity_icrf_km_s',[float('nan'),1,2]),
            ('rotation_icrf_to_true_ecliptic',[[1,0,0],[0,2,0],[0,0,1]]),
            ('rotation_icrf_to_true_ecliptic',[[-1,0,0],[0,1,0],[0,0,1]])):
            item=copy.deepcopy(s);item[field]=value
            with self.assertRaises(ValueError):osculating_apogee(item['position_icrf_km'],item['velocity_icrf_km_s'],item['rotation_icrf_to_true_ecliptic'])

    def test_osculating_velocity_units_error_is_not_accepted(self):
        s=lunar_state();v=[x*86400 for x in s['velocity_icrf_km_s']]
        with self.assertRaises(ValueError):osculating_apogee(s['position_icrf_km'],v,s['rotation_icrf_to_true_ecliptic'])

    def test_axis_continuity_across_pole_flip_and_wraparound(self):
        self.assertEqual(axis_sample_longitude(180,0),0)
        self.assertEqual(axis_sample_longitude(0,179),180)
        self.assertEqual(axis_sample_longitude(359,179),179)

    def test_precision_policy_checks_identical_input_scope_not_external_validation(self):
        policy=json.loads((ROOT/'src/almas_tfa/data/ssar-calculated-points-precision-policy.json').read_text())
        self.assertEqual(set(policy['tolerances_deg'].values()),{1e-7})
        self.assertEqual(policy['external_validation_status'],'NOT_PERFORMED')
        self.assertIn('IDENTICAL_INPUTS',policy['scope'])
