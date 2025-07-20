import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class PDFGenerator:
    def __init__(self, output_dir="pdf-docs"):
        self.output_dir = output_dir
        self.ensure_directory()
    
    def ensure_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def create_pdf(self, filename, text_content):
        filepath = os.path.join(self.output_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)
        width, height = letter
        
        c.drawString(100, height - 100, text_content)
        c.save()
        
        return filepath
    
    def generate_batch(self, count=20):
        generated_files = []
        
        for i in range(1, count + 1):
            filename = f"pdf-{i}.pdf"
            text_content = filename
            
            filepath = self.create_pdf(filename, text_content)
            generated_files.append(filepath)
            
            print(f"Создан файл: {filepath}")
        
        return generated_files

def main():
    generator = PDFGenerator()
    files = generator.generate_batch(20)
    print(f"\nВсего создано файлов: {len(files)}")

if __name__ == "__main__":
    main()
