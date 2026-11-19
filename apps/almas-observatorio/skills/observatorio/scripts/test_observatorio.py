import copy
from datetime import date
import json
from pathlib import Path
import unittest
from observatorio import separation, validate, run
from culminaciones import roots

class DailyTests(unittest.TestCase):
    folder=Path(__file__).resolve().parents[5]/"data/public-asteroid-ephemerides"

    def test_wrap(self):
        self.assertAlmostEqual(separation(359.9,.1),.2)

    def test_root_and_tangent(self):
        self.assertEqual(roots(lambda x:(x-2,1),[0,4]),[2])
        self.assertEqual(roots(lambda x:((x-2)**2,2*x-4),[0,4]),[2])
        self.assertEqual(roots(lambda x:((179+x+180)%360-180,1),[0,4]),[])

    def test_public_file(self):
        if not self.folder.exists():
            self.skipTest("requiere checkout ALMAS")
        sample=date(2026,11,19)
        doc=json.loads((self.folder/f"{sample}.json").read_text())
        self.assertEqual(len(validate(doc,sample)[str(sample)]),19)
        for key,value in [("flags_returned",260),("longitude_deg",float("nan")),("speed_deg_per_day",None)]:
            broken=copy.deepcopy(doc)
            broken["asteroids"]["2847"]["positions"][str(sample)][key]=value
            with self.assertRaises(ValueError):
                validate(broken,sample)

    def test_historical_window(self):
        if not self.folder.exists():
            self.skipTest("requiere checkout ALMAS")
        result=run(self.folder,date(2026,11,15))
        self.assertEqual(sum(result["cobertura"].values()),11)
        self.assertEqual(result["vinculo"],None)
