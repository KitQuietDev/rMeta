## Third-Party Libraries Used in rMeta

This document lists all third-party libraries used in rMeta, along with their license types and compatibility with rMeta's MIT license.

| Library           | Purpose                          | License         | MIT-Compatible | Notes                                         |
|-------------------|----------------------------------|------------------|----------------|----------------------------------------------|
| python-docx       | Word document parsing            | MIT              | ✅ Yes         | Used in `docx_handler.py`                     |
| openpyxl          | Excel file parsing               | MIT              | ✅ Yes         | Used in `excel_handler.py`                    |
| pdfplumber        | PDF text extraction              | MIT              | ✅ Yes         | Used in `pdf_handler.py`                      |
| pandas            | Data manipulation                | BSD-3-Clause     | ✅ Yes         | Used in shared utilities                      |
| numpy             | Numerical operations             | BSD-3-Clause     | ✅ Yes         | Used in shared utilities                      |
| requests          | HTTP requests                    | Apache-2.0       | ✅ Yes         | Used in `app.py` or integrations              |
| Flask             | Web framework                    | BSD-3-Clause     | ✅ Yes         | Used in `app.py`                              |
| pytest            | Testing framework                | MIT              | ✅ Yes         | Dev-only                                      |
| coverage          | Test coverage reporting          | Apache-2.0       | ✅ Yes         | Dev-only                                      |
| python-dotenv     | Environment variable loading     | BSD-3-Clause     | ✅ Yes         | Used in config setup                          |
| tqdm              | Progress bars                    | MIT              | ✅ Yes         | Optional UX enhancement                       |
| chardet           | Encoding detection               | LGPL-2.1         | ⚠️ Yes         | Permissive; **requires attribution notice**   |
| typing-extensions | Type hinting support             | PSF              | ✅ Yes         | Used for type compatibility                   |

## Special Notices

- **chardet** is licensed under the LGPL-2.1. While LGPL is generally permissive, it requires that users be informed of their rights under the license and must retain attribution notices. rMeta complies by documenting usage and respecting redistribution terms.

We thank the maintainers of these libraries for their contributions to the open-source ecosystem.
