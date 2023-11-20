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
        self.isa_attributes = {
            "identifier": ome_project.getName().lower().replace(" ", "-"),
            "title": ome_project.getName(),
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
