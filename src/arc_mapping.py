import importlib


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
        self.isa_attributes = {
            "ARC:ISA:STUDY:STUDY METADATA": {
                "defaults": {
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
            "ARC:ISA:STUDY:STUDY PUBLICATIONS": {
                "defaults": {
                    "Study Publication DOI": None,
                    "Study Publication PubMed ID": None,
                    "Study Publication Author List": None,
                    "Study Publication Title": None,
                    "Study Publication Status": None,
                    "Study Publication Status Term Accession Number": None,
                    "Study Publication Status Term Source REF": None,
                },
                "command": ["arc", "study", "publication", "register"],
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
            "ARC:ISA:STUDY:STUDY DESIGN DESCRIPTORS": {
                "Study Design Type": None,
                "Study Design Type Term Accession Number": None,
                "Study Design Type Term Accession Number": None,
            },
            "ARC:ISA:STUDY:STUDY FACTORS": {
                "Study Factor Name": None,
                "Study Factor Type": None,
                "Study Design Type Term Accession Number": None,
                "Study Design Type Term Accession Number": None,
            },
            "ARC:ISA:STUDY:STUDY PROTOCOLS": {
                "Study Protocol Name": None,
                "Study Protocol Type": None,
                "Study Protocol Term Accession Number": None,
                "Study Protocol Term Source REF": None,
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
            "ARC:ISA:STUDY:STUDY CONTACTS": {
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
        }

        self.arccommander_mapping = {
            "--identifier": "Study Identifier",
            "--title": "Study Title",
            "--description": "Study Description",
            "--submissiondate": "Study Submission Date",
            "--publicreleasedate": "Study Public Release Date",
        }


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
