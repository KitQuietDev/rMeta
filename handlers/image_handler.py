import piexif

supported_extensions = {"jpg", "jpeg", "png"}

def scrub(file_path):
    try:
        piexif.remove(file_path)
    except Exception as e:
        print(f"Error scrubbing image metadata: {e}")
