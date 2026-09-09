import unittest

from book_mobility_program_data.capture import normalize
from book_mobility_program_data.cli import resource, validate


class SourceTests(unittest.TestCase):
    def raw(self):
        return (
            "<h1>Rules of the DiscoverEU call for applications</h1>"
            "<p>In autumn 2026, the European Commission plans to award around 40 000 young people with travel passes and discount cards.</p>"
            "<p>The application period is planned from 1 October 2026 to 15 October 2026.</p>"
            "<p>Travel is available between 1 March 2027 and 31 May 2028.</p>"
            "<h2>Eligible applicants</h2>"
            "<p>Applicants must have celebrated their 18th birthday in 2026.</p>"
        ).encode("utf-8")

    def test_discovereu_source_fixture(self):
        source = resource("source.json")
        data = normalize(self.raw(), source, "2026-09-07T00:00:00Z")
        item = data["items"][0]
        item["provenance"].update(
            raw_object_key="landing/test",
            bronze_manifest_key="control/manifests/test",
        )
        self.assertEqual(item["title"], "DiscoverEU autumn 2026 travel pass")
        self.assertEqual(item["status"], "open")
        self.assertEqual(item["deadline"]["at"], "2026-10-15T12:00:00+02:00")
        self.assertEqual(item["terms"]["destination_country"], "MULTI")
        self.assertEqual(item["value"]["kind"], "access")
        self.assertEqual(validate(data)["schema_version"], source["schema_version"])

    def test_source_drift_rejected(self):
        with self.assertRaises(ValueError):
            normalize(b"<h1>unrelated page</h1>", resource("source.json"), "2026-09-07T00:00:00Z")

    def test_additional_mobility_sources_normalize(self):
        fixtures = {
            "source-erasmus-youth-exchanges.json": (
                "Mobility projects for young people - Youth Exchanges; groups from different countries."
            ),
            "source-european-solidarity-corps-volunteering.json": (
                "European Solidarity Corps volunteering projects help volunteers abroad."
            ),
            "source-culture-moves-europe-residency-hosts.json": (
                "Call for residency hosts provides financial support for a residency project."
            ),
            "source-cost-eu-resolve-conference-grants.json": (
                "EU-RESOLVE Conference Grants 2026 include a travel grant for young researchers."
            ),
        }
        for filename, text in fixtures.items():
            with self.subTest(source=filename):
                source = resource(filename)
                data = normalize(f"<p>{text}</p>".encode(), source, "2026-09-08T00:00:00Z")
                item = data["items"][0]
                item["provenance"].update(raw_object_key="landing/test", bronze_manifest_key="control/manifests/test")
                self.assertEqual(item["category"], source["category"])
                self.assertEqual(validate(data)["schema_version"], "mobility_program.v1")


if __name__ == "__main__": unittest.main()
