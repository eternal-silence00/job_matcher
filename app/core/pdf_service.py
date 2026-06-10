from pypdf import PdfReader

class PdfService:
    def extract_text(self, file) -> str:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text