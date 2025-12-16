"""
Módulo para extração de texto de arquivos PDF
"""
import fitz
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class PageContent:
    """Representa o conteúdo de uma página"""
    text: str
    page_number: int
    total_characters: int
    metadata: Dict[str, any]


@dataclass
class PDFDocument:
    """Representa um documento PDF completo"""
    filepath: Path
    pages: List[PageContent]
    metadata: Dict[str, any]
    
    @property
    def total_pages(self) -> int:
        return len(self.pages)
    
    @property
    def total_characters(self) -> int:
        return sum(p.total_characters for p in self.pages)


class PDFExtractor:
    """Extrai texto de arquivos PDF"""
    
    def __init__(self):
        pass
    
    def extract_from_file(self, filepath: str | Path) -> PDFDocument:
        """
        Extrai texto de um arquivo PDF
        
        Args:
            filepath: Caminho para o arquivo PDF
            
        Returns:
            PDFDocument com texto e metadados
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"PDF não encontrado: {filepath}")
        
        if not filepath.suffix.lower() == '.pdf':
            raise ValueError(f"Arquivo não é PDF: {filepath}")
        
        try:
            doc = fitz.open(filepath)
            
            # Extrai metadados do documento
            metadata = {
                "title": doc.metadata.get("title", filepath.stem),
                "author": doc.metadata.get("author", "Desconhecido"),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "creation_date": doc.metadata.get("creationDate", ""),
                "mod_date": doc.metadata.get("modDate", ""),
                "filepath": str(filepath),
                "filename": filepath.name,
                "file_hash": self._compute_file_hash(filepath)
            }
            
            # Extrai texto de cada página
            pages = []
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text("text")
                
                # Limpa o texto
                cleaned_text = self._clean_text(text)
                
                if cleaned_text.strip():
                    page_content = PageContent(
                        text=cleaned_text,
                        page_number=page_num,
                        total_characters=len(cleaned_text),
                        metadata={
                            "page_number": page_num,
                            "filename": filepath.name
                        }
                    )
                    pages.append(page_content)
            
            doc.close()
            
            if not pages:
                raise ValueError(f"Nenhum texto extraído do PDF: {filepath}")
            
            return PDFDocument(
                filepath=filepath,
                pages=pages,
                metadata=metadata
            )
            
        except Exception as e:
            raise Exception(f"Erro ao processar PDF {filepath}: {e}")
    
    def extract_from_directory(
        self, 
        directory: str | Path,
        recursive: bool = False
    ) -> List[PDFDocument]:
        """
        Extrai texto de todos os PDFs em um diretório
        
        Args:
            directory: Caminho do diretório
            recursive: Se True, procura em subdiretórios
            
        Returns:
            Lista de PDFDocuments
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise FileNotFoundError(f"Diretório não encontrado: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Caminho não é um diretório: {directory}")
        
        # Encontra todos os PDFs
        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdf_files = list(directory.glob(pattern))
        
        if not pdf_files:
            raise ValueError(f"Nenhum PDF encontrado em: {directory}")
        
        documents = []
        errors = []
        
        for pdf_file in pdf_files:
            try:
                doc = self.extract_from_file(pdf_file)
                documents.append(doc)
            except Exception as e:
                errors.append({
                    "file": str(pdf_file),
                    "error": str(e)
                })
        
        if errors:
            print(f"⚠️  Erros ao processar {len(errors)} arquivo(s):")
            for error in errors:
                print(f"  - {error['file']}: {error['error']}")
        
        return documents
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Limpa e normaliza o texto extraído"""
        # Remove linhas vazias excessivas
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)
        
        # Remove espaços múltiplos
        import re
        cleaned = re.sub(r' +', ' ', cleaned)
        
        return cleaned
    
    @staticmethod
    def _compute_file_hash(filepath: Path) -> str:
        """Computa hash MD5 do arquivo"""
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()