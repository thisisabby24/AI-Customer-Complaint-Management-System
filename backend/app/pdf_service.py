from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(
    file_bytes: bytes
) -> str:

    if not file_bytes:
        raise ValueError(
            "The uploaded PDF is empty."
        )

    try:

        pdf_file = BytesIO(
            file_bytes
        )

        reader = PdfReader(
            pdf_file
        )

        pages_text = []


        for page in reader.pages:

            text = page.extract_text()

            if text:

                pages_text.append(
                    text
                )


        full_text = "\n".join(
            pages_text
        ).strip()


        if not full_text:

            raise ValueError(
                "No readable text was found in the PDF."
            )


        return full_text


    except Exception as e:

        raise ValueError(
            f"Could not read PDF: {str(e)}"
        )