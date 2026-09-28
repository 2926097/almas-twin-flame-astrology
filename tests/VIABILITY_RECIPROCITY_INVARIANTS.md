# Invariantes · M29 viabilidad y reciprocidad factual

Una release falla si:

1. M29 acepta una viabilidad evaluada sin eventos `VIABILITY_FACT` elegibles.
2. M29 acepta una reciprocidad evaluada sin eventos `RECIPROCITY_FACT` elegibles.
3. Un evento `SUPERSEDED` puede sostener el estado actual.
4. Un evento con contrato documental fallido puede sostener M29.
5. `DQ4_SECONDARY_REPORT` o `DQ5_UNVERIFIED` bastan por sí solos para una clasificación fuerte.
6. Un evento posterior a `as_of_date` se usa para describir el estado anterior cuando su fecha es ordenable.
7. La base factual evaluada no cubre a ambos sujetos.
8. La ausencia de evidencia de una parte se convierte en `ASYMMETRIC`.
9. `DOCUMENTED_SEPARATION` se acepta sin `event_type=SEPARATION`.
10. `DOCUMENTED_NO_CONTACT` se acepta sin `event_type=NO_CONTACT`.
11. PHASE determina automáticamente REAL_VIABILITY.
12. Reciprocidad astrológica sustituye RECIPROCITY interpersonal.
13. Fenomenología subjetiva sustituye un `RECIPROCITY_FACT`.
14. Una hipótesis metafísica se usa como hecho interpersonal.
15. M29 infiere pensamientos, sentimientos, consentimiento, fidelidad o decisiones futuras.
16. `UNKNOWN` o `NOT_EVALUABLE` se presentan como evidencia positiva de un estado.
