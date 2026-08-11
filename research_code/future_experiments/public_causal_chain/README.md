# Public causal-chain pilot

This module is a fail-closed research Seam for testing whether a language model
can turn **public, cited mechanism facts** into numeric features.

- Input: `PublicEvidencePacket` containing 1--16 canonical JSON facts. Arbitrary
  prose, file paths, vectors and private-competition scope are rejected.
- Output: 3--8 `source -> relation -> mechanism axis` edges. The target vocabulary
  is frozen to 23 interpretable axes; no protein or expression vector is emitted.
- Implementations: deterministic fixture, loopback-only Ollama, and an optional
  OpenAI public-only Adapter that is disabled by default.

The offline tests and the RNA mini-pilot never call an external model. Enabling
the OpenAI Adapter is a separate, explicit future action and still cannot pass
the private competition matrix through this Interface.
