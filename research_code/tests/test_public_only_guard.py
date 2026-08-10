import unittest

from future_experiments import EvidenceScope, PublicEvidencePacket, PublicOnlyGuard


class PublicOnlyGuardTest(unittest.TestCase):
    def test_accepts_public_aggregate_evidence(self) -> None:
        packet = PublicEvidencePacket(
            entity="rapamycin",
            scope=EvidenceScope.PUBLIC,
            facts=("targets TOR signaling",),
            citations=("public:test",),
        )
        PublicOnlyGuard().validate(packet)

    def test_rejects_private_or_vector_payloads(self) -> None:
        private = PublicEvidencePacket(
            entity="anonymous-compound",
            scope=EvidenceScope.PRIVATE_COMPETITION,
            facts=("private response",),
            citations=(),
        )
        with self.assertRaises(ValueError):
            PublicOnlyGuard().validate(private)

        vector = PublicEvidencePacket(
            entity="public compound",
            scope=EvidenceScope.PUBLIC,
            facts=("protein_vector=[1,2,3]",),
            citations=("public:test",),
        )
        with self.assertRaises(ValueError):
            PublicOnlyGuard().validate(vector)


if __name__ == "__main__":
    unittest.main()
