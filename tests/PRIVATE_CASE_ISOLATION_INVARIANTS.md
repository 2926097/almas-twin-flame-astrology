# Invariantes · Aislamiento de casos privados

1. La política canónica es `ALMAS_PUBLIC_DATA_ISOLATION_V1`.
2. `examples/` sólo admite `SYNTHETIC`.
3. `public_cases/` sólo admite `PUBLIC_VERIFIABLE`.
4. `validation/holdouts/` sólo admite `SYNTHETIC`, `PUBLIC_VERIFIABLE` o `PUBLIC_METADATA_ONLY`.
5. Todo JSON público de esos scopes debe estar registrado exactamente una vez en su manifiesto.
6. Un fixture sintético mantiene `contains_real_person_data=false`.
7. Un fixture sintético mantiene `contains_nonpublic_material=false`.
8. Un fixture sintético mantiene `derived_from_private_case=false`.
9. Un fixture sintético mantiene `reversible_from_private_case=false`.
10. Un caso público verificable exige `public_source_refs` no vacío.
11. Un caso público verificable exige `independently_verifiable=true`.
12. `PRIVATE_CASE` no puede publicarse.
13. `PSEUDONYMIZED_PRIVATE` no puede publicarse.
14. `PRIVATE_HOLDOUT` no puede publicarse.
15. `CONFIDENTIAL` no puede publicarse.
16. La pseudonimización no convierte un caso privado en público.
17. Ninguna ruta privada reservada puede existir en el checkout público.
18. Las rutas privadas reservadas deben permanecer ignoradas por Git.
19. Un holdout privado sólo puede vivir fuera del repositorio público.
20. El repositorio no publica hashes reversibles de datos personales como sustituto del aislamiento.
21. `PRIVACY_BREACH` invalida el artefacto público afectado.
22. Superar el gate de privacidad no añade peso ontológico ni aumenta IRC.
