from abstract_arc_test import AbstractArcTest
from arc_mapping import IsaInvestigationMapper


class TestIsaInvestigationMapper(AbstractArcTest):
    def test_investigation_isa_attributes(
        self, project_with_arc_assay_annotation, project_1
    ):
        p = project_1
        pa = project_with_arc_assay_annotation

        m = IsaInvestigationMapper(p)
        ma = IsaInvestigationMapper(pa)

        # assert (
        #     len(m.isa_attributes["ontology_source_reference"]["values"]) == 0
        # )

        assert (
            len(ma.isa_attributes["ontology_source_reference"]["values"]) == 2
        )

        assert ma.isa_attributes["ontology_source_reference"]["values"][0][
            "Term Source Name"
        ] in ("SCoRO", "EFO")
        assert ma.isa_attributes["ontology_source_reference"]["values"][1][
            "Term Source Name"
        ] in ("SCoRO", "EFO")
        assert ma.isa_attributes["ontology_source_reference"]["values"][0][
            "Term Source Description"
        ] in (
            "SCoRO, the Scholarly Contributions and Roles Ontology",
            "Experimental Factor Ontology",
        )
        assert ma.isa_attributes["ontology_source_reference"]["values"][1][
            "Term Source Description"
        ] in (
            "SCoRO, the Scholarly Contributions and Roles Ontology",
            "Experimental Factor Ontology",
        )

        assert len(ma.isa_attributes["investigation"]["values"]) == 1
        assert len(m.isa_attributes["investigation"]["values"]) == 1

        assert (
            m.isa_attributes["investigation"]["values"][0][
                "Investigation Identifier"
            ]
            == "default-investigation-id"
        )

        assert (
            ma.isa_attributes["investigation"]["values"][0][
                "Investigation Identifier"
            ]
            == "my-custom-investigation-id"
        )

        assert (
            ma.isa_attributes["investigation"]["values"][0][
                "Investigation Title"
            ]
            == "Mitochondria in HeLa Cells"
        )
