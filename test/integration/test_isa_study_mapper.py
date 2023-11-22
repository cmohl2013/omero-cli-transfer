from abstract_arc_test import AbstractArcTest
from arc_mapping import IsaStudyMapper


class TestIsaStudyMapper(AbstractArcTest):
    def test_isa_attributes(
        self, project_with_arc_assay_annotation, project_1
    ):
        p = project_1
        pa = project_with_arc_assay_annotation

        mapper_1 = IsaStudyMapper(p)
        assert (
            mapper_1.isa_attributes["metadata"]["values"][0][
                "Study Identifier"
            ]
            == "my-first-study"
        )
        assert (
            mapper_1.isa_attributes["metadata"]["values"][0]["Study Title"]
            == "My First Study"
        )

        mapper_2 = IsaStudyMapper(pa)
        assert (
            mapper_2.isa_attributes["metadata"]["values"][0][
                "Study Identifier"
            ]
            == "my-custom-study-id"
        )
        assert (
            mapper_2.isa_attributes["metadata"]["values"][0]["Study Title"]
            == "My Custom Study Title"
        )

    def test_annotation_data(
        self, project_1, project_with_arc_assay_annotation
    ):
        p = project_1
        pa = project_with_arc_assay_annotation

        mapper_1 = IsaStudyMapper(p)
        annotation_data = mapper_1._annotation_data("metadata")
        assert len(annotation_data) == 0

        mapper_2 = IsaStudyMapper(pa)
        annotation_data = mapper_2._annotation_data("metadata")
        assert len(annotation_data) == 1
        assert annotation_data[0]["Study Title"] == "My Custom Study Title"
