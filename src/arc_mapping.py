import importlib
from functools import lru_cache

if importlib.util.find_spec("pandas"):
    import pandas as pd
else:
    raise ImportError(
        "Could not import pandas library. Make sure to "
        "install omero-cli-transfer with the optional "
        "[arc] addition"
    )


class AbstractIsaAssaySheetMapper:
    def __init__(self, ome_dataset):
        self.ome_dataset = ome_dataset

    def tbl(self, conn):
        objs = conn.getObjects(
            self.obj_type, opts={"dataset": self.ome_dataset.getId()}
        )
        objs = [obj for obj in objs]

        rows = [self.isa_column_mapping(obj) for obj in objs]
        df = pd.DataFrame(rows)
        df.name = self.sheet_name
        return df


class IsaStudyMapper:
    def __init__(self, ome_project):
        self.obj = ome_project

        # annotation
        self.isa_attribute_config = {
            "metadata": {
                "namespace": "ARC:ISA:STUDY:STUDY METADATA",
                "default_values": {
                    "Study Identifier": ome_project.getName()
                    .lower()
                    .replace(" ", "-"),
                    "Study Title": ome_project.getName(),
                    "Study Description": ome_project.getDescription(),
                    "Study Submission Date": None,
                    "Study Public Release Date": None,
                },
                "command": ["arc", "study", "add"],
                "command_options": {
                    "Study Identifier": "--identifier",
                    "Study Title": "--title",
                    "Study Description": "--description",
                    "Study Submission Date": "--submissiondate",
                    "Study Public Release Date": "--publicreleasedate",
                },
            },
            "publications": {
                "namespace": "ARC:ISA:STUDY:STUDY PUBLICATIONS",
                "default_values": {
                    "Study Publication DOI": None,
                    "Study Publication PubMed ID": None,
                    "Study Publication Author List": None,
                    "Study Publication Title": None,
                    "Study Publication Status": None,
                    "Study Publication Status Term Accession Number": None,
                    "Study Publication Status Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "publication",
                    "register",
                ],
                "command_options": {
                    "Study Publication DOI": "--doi",
                    "Study Publication PubMed ID": "--pubmedid",
                    "Study Publication Author List": "--authorlist",
                    "Study Publication Title": "--title",
                    "Study Publication Status": "--status",
                    "Study Publication Status Term Accession Number": "--statustermaccessionnumber",
                    "Study Publication Status Term Source REF": "--statustermsourceref",
                },
            },
            "design": {
                "namespace": "ARC:ISA:STUDY:STUDY DESIGN DESCRIPTORS",
                "default_values": {
                    "Study Design Type": None,
                    "Study Design Type Term Accession Number": None,
                    "Study Design Type Term Accession Number": None,
                },
                "command": [
                    "arc",
                    "study",
                    "design",
                    "register",
                ],
                "command_options": {
                    "Study Design Type": "--designtype",
                    "Study Design Type Term Accession Number": "--typetermaccessionnumber",
                    "Study Design Type Term Accession Number": "--typetermsourceref",
                },
            },
            "factors": {
                "namespace": "ARC:ISA:STUDY:STUDY FACTORS",
                "default_values": {
                    "Study Factor Name": None,
                    "Study Factor Type": None,
                    "Study Design Type Term Accession Number": None,
                    "Study Design Type Term Accession Number": None,
                },
                "command": [
                    "arc",
                    "study",
                    "factor",
                    "register",
                ],
                "command_options": {
                    "Study Factor Name": "--name",
                    "Study Factor Type": "--factortype",
                    "Study Design Type Term Accession Number": "--typetermaccessionnumber",
                    "Study Design Type Term Accession Number": "--typetermsourceref",
                },
            },
            "protocols": {
                "namespace": "ARC:ISA:STUDY:STUDY PROTOCOLS",
                "default_values": {
                    "Study Protocol Name": None,
                    "Study Protocol Type": None,
                    "Study Protocol Type Term Accession Number": None,
                    "Study Protocol Type Term Source REF": None,
                    "Study Protocol Description": None,
                    "Study Protocol URI": None,
                    "Study Protocol Version": None,
                    "Study Protocol Parameters Name": None,
                    "Study Protocol Parameters Term Accession Number": None,
                    "Study Protocol Parameters Term Source REF": None,
                    "Study Protocol Components Name": None,
                    "Study Protocol Components Type": None,
                    "Study Protocol Components Term Accession Number": None,
                    "Study Protocol Components Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "protocol",
                    "register",
                ],
                "command_options": {
                    "Study Protocol Name": "--name",
                    "Study Protocol Type": "--protocoltype",
                    "Study Protocol Type Term Accession Number": "--typetermaccessionnumber",
                    "Study Protocol Type Term Source REF": "--typetermsourceref",
                    "Study Protocol Description": "--description",
                    "Study Protocol URI": "--uri",
                    "Study Protocol Version": "--version",
                    "Study Protocol Parameters Name": "--parametersname",
                    "Study Protocol Parameters Term Accession Number": "--parameterstermaccessionnumber",
                    "Study Protocol Parameters Term Source REF": "--parameterstermsourceref",
                    "Study Protocol Components Name": "--componentsname",
                    "Study Protocol Components Type": "--componentstype",
                    "Study Protocol Components Term Accession Number": "--componentstypeaccessionnumber",
                    "Study Protocol Components Term Source REF": "--componentstypetermsourceref",
                },
            },
            "contacts": {
                "namespace": "ARC:ISA:STUDY:STUDY CONTACTS",
                "default_values": {
                    "Study Person Last Name": None,
                    "Study Person First Name": None,
                    "Study Person Email": None,
                    "Study Person Phone": None,
                    "Study Person Fax": None,
                    "Study Person Address": None,
                    "Study Person Affiliation": None,
                    "Study Person orcid": None,
                    "Study Person Roles": None,
                    "Study Person Roles Term Accession Number": None,
                    "Study Person Roles Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "person",
                    "register",
                ],
                "command_options": {
                    "Study Person Last Name": "--lastname",
                    "Study Person First Name": "--firstname",
                    "Study Person Mid Initials": "--midinitials",
                    "Study Person Email": "--email",
                    "Study Person Phone": "--phone",
                    "Study Person Fax": "--fax",
                    "Study Person Address": "--address",
                    "Study Person Affiliation": "--affiliation",
                    "Study Person orcid": "--orcid",
                    "Study Person Roles": "--roles",
                    "Study Person Roles Term Accession Number": "--rolestermaccessionnumber",
                    "Study Person Roles Term Source REF": "--rolestermsourceref",
                },
            },
        }

        self._create_isa_attributes()

    @lru_cache
    def _all_annotatation_objects(self):
        return [a for a in self.obj.listAnnotations()]

    def _annotation_data(self, annotation_type):
        namespace = self.isa_attribute_config[annotation_type]["namespace"]
        annotation_data = []
        for annotation in self._all_annotatation_objects():
            if annotation.getName() == namespace:
                annotation_data.append(dict(annotation.getValue()))
        return annotation_data

    def _create_isa_attributes(self):
        isa_attributes = {}
        for annotation_type in self.isa_attribute_config:
            annotation_data = self._annotation_data(annotation_type)
            config = self.isa_attribute_config[annotation_type]

            isa_attributes[annotation_type] = {}

            if annotation_type == "metadata":
                assert (
                    len(annotation_data) <= 1
                ), f"only one annotation allowed for {config['namespace']}"
                command = config["command"]
            else:
                command = config["command"] + [
                    "--studyidentifier",
                    self.study_identifier(),
                ]

            isa_attributes[annotation_type]["values"] = []
            isa_attributes[annotation_type]["command"] = command
            isa_attributes[annotation_type]["command_options"] = config[
                "command_options"
            ]
            values_to_set = {}
            if len(annotation_data) == 0:
                # set defaults if no annotations available
                for key in config["default_values"]:
                    value = config["default_values"][key]
                    if value is not None:
                        values_to_set[key] = value
                isa_attributes[annotation_type]["values"].append(values_to_set)
            else:
                # set defaults only for keys where no annotation is available
                for annotation in annotation_data:
                    for key in config["default_values"]:
                        value = annotation.get(key, None)
                        if value is None:
                            value = config["default_values"][key]
                        if value is not None:
                            values_to_set[key] = value
                    isa_attributes[annotation_type]["values"].append(
                        values_to_set
                    )

            self.isa_attributes = isa_attributes

    def study_identifier(self):
        return self.isa_attributes["metadata"]["values"][0]["Study Identifier"]


class IsaAssayMapper:
    def __init__(self, ome_dataset, image_filename_getter):
        self.image_filename_getter = image_filename_getter

        def _measurementtype():
            return "Microscopy"

        def _fmt_identifier(name):
            return name.lower().replace(" ", "-")

        self.isa_attributes_mapping = {
            "assayidentifier": _fmt_identifier(ome_dataset.getName()),
            "measurementtype": _measurementtype(),
        }

        self.isa_sheets = [
            IsaAssaySheetImageFilesMapper(
                ome_dataset, self.image_filename_getter
            ),
            IsaAssaySheetImageMetadataMapper(ome_dataset),
        ]


class IsaAssaySheetImageFilesMapper(AbstractIsaAssaySheetMapper):
    def __init__(self, ome_dataset, image_filename_getter):
        self.obj_type = "Image"
        self.sheet_name = "Image Files"
        self.image_filename_getter = image_filename_getter

        super().__init__(ome_dataset)

    def isa_column_mapping(self, image):
        isa_column_mapping = {
            "Image ID": image.getId(),
            "Name": image.getName(),
            "Description": image.getDescription(),
            "Filename": self.image_filename_getter(
                image.getId(), abspath=False
            ),
        }
        return isa_column_mapping


class IsaAssaySheetImageMetadataMapper(AbstractIsaAssaySheetMapper):
    def __init__(self, ome_dataset):
        self.obj_type = "Image"
        self.sheet_name = "Image Metadata"
        super().__init__(ome_dataset)

    def isa_column_mapping(self, image):
        def _pixel_unit(image):
            pix = image.getPixelSizeX(units=True)
            if pix is None:
                return
            return pix.getUnit()

        isa_column_mapping = {
            "Image ID": image.getId(),
            "Image Size X": image.getSizeX(),
            "Image Size Y": image.getSizeY(),
            "Image Size Z": image.getSizeZ(),
            "Pixel Size X": image.getPixelSizeX(),
            "Pixel Size Y": image.getPixelSizeY(),
            "Pixel Size Z": image.getPixelSizeZ(),
            "Pixel Size Unit": _pixel_unit(image),
        }
        return isa_column_mapping
