from openpyxl import load_workbook

supported_extensions = {"xlsx"}

def scrub(file_path):
    try:
        wb = load_workbook(file_path)
        props = wb.properties

        # Clear common metadata fields
        props.title = None
        props.subject = None
        props.creator = None
        props.keywords = None
        props.description = None
        props.lastModifiedBy = None
        props.category = None
        props.contentStatus = None
        props.created = None
        props.modified = None

        wb.save(file_path)
    except Exception as e:
        print(f"Error scrubbing XLSX metadata: {e}")
