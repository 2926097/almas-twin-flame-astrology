# Invariantes · Doctrinal Claim v2

1. Todo claim importante usa `schema_version=2.0.0`.
2. `source_ids` y `source_anchor_refs` deben referenciar fuentes existentes cuando el claim depende de fuentes.
3. Todo anclaje material posee `verification_anchor`, `verification_anchor_type` y `evidence_scope`.
4. `ceiling_enforced` siempre es `true`.
5. `requested_conclusion` puede ser más fuerte que `allowed_conclusion`, pero la narrativa sólo publica `allowed_conclusion`.
6. Si `discriminator_state=NOT_VALIDATED`, un upgrade dependiente de ese discriminador no puede publicarse como `SUPPORTED`.
7. `C_DOCTRINE` no hereda una operacionalización astrológica como si fuera doctrina.
8. `C_DOCTRINE + DIRECT_DOCTRINE` exige `source_support_refs` y `does_not_support_checked=true`.
9. `B_TECHNIQUE` puede estar `SUPPORTED` para el cálculo mientras la ontología permanece `INSUFFICIENT`.
10. `D_CONTEMPORARY_USAGE` no eleva ORIGIN ni PREINCARNATION_CONTRACT.
11. `E_PROJECT_HYPOTHESIS` declara alternativas cuando solicita una conclusión específica.
12. Una hipótesis del proyecto no puede usar `DIRECT_DOCTRINE`.
13. `asserts_doctrinal_identity=true` exige `identity_target_concept_id`.
14. Una relación `NON_EQUIVALENT` para el par declarado impide afirmar identidad doctrinal.
15. Ningún claim doctrinal añade puntuación estructural por cantidad de fuentes.
