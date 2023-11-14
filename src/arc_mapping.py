class IsaStudyMapper:
    def __init__(self, ome_project):
        self.obj = ome_project
        self.isa_attributes = {
            "identifier": self.obj.getName().lower().replace(" ", "-"),
            "title": self.obj.getName(),
        }


class IsaAssayMapper:
    def __init__(self, ome_dataset, image_filename_getter):
        self.image_filename_getter = image_filename_getter

        def _measurementtype():
            # measurementtype = (
            #     ome_dataset.getAnnotations(filter="namespace == 'isa.assay'")[
            #         0
            #     ].getValue("measurementtype"),
            # )
            # if measurementtype is None:
            return "Microscopy"

        self.isa_attributes_mapping = {
            "assayidentifier": ome_dataset.getName().lower().replace(" ", "-"),
            "measurementtype": _measurementtype(),
        }

        self.isa_sheets = [
            IsaAssaySheetImageFilesMapper(
                ome_dataset, self.image_filename_getter
            ),
            IsaAssaySheetImageMetadataMapper(ome_dataset),
        ]


class IsaAssaySheetImageFilesMapper:
    def __init__(self, ome_dataset, image_filename_getter):
        self.sheet_name = "Image Files"
        self.ome_dataset = ome_dataset
        self.image_filename_getter = image_filename_getter

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


class IsaAssaySheetImageMetadataMapper:
    def __init__(self, ome_dataset):
        self.sheet_name = "Image Metadata"
        self.ome_dataset = ome_dataset

    def isa_column_mapping(self, image):
        isa_column_mapping = {
            "Image ID": image.getId(),
            "Image Size X": image.getSizeX(),
            "Image Size Y": image.getSizeY(),
            "Image Size Z": image.getSizeZ(),
            "Pixel Size X": image.getPixelSizeX.getValue(),
            "Pixel Size Y": image.getPixelSizeY.getValue(),
            "Pixel Size Z": image.getPixelSizeZ.getValue(),
            "Pixel Size Unit": image.getPixelSizeX.getValue(
                units=True
            ).getSymol(),
        }
        return isa_column_mapping
