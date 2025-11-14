# MODULES (EXTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
from typing import List, Optional
# ---------------------------------------------------------------------------------------------------------------------

# MODULES (INTERNAL)
# ---------------------------------------------------------------------------------------------------------------------
# Get listed here!
# ---------------------------------------------------------------------------------------------------------------------

# OPERATIONS / CLASS CREATION / GENERAL FUNCTIONS
# ---------------------------------------------------------------------------------------------------------------------

__all__ = ['DocStrings']

class DocStrings:
    """
    Helper class for formatting docstrings.
    """
    
    @classmethod
    def to_readme(cls, doc: str, *, tabulation: bool = True, cleaned: Optional[List[str]] = None) -> str:
        """
        Applies the full format to the received text (docstring) by combining 
        the tabulation and cleanup steps.

        This method acts as a central entry point for normalizing the presentation 
        of docstrings before adding them to the README or other generated output.

        Args:
            doc (str):
                Original text of the docstring to be formatted.
            tabulation (bool): 
                If True, adds "\\t" to the beginning of each line.
            cleaned (List[str], optional): 
                List of tokens to be removed using replace.

        Returns:
            str:
                Text resulting after applying the format.

        Raises:
            TypeError:
                If `cleaned` is provided but is not a list.
            ValueError:
                If `cleaned` is not provided.
        """
        if tabulation:
            doc = cls.__tabulation(doc)

        if cleaned:
            if not isinstance(cleaned, list):
                raise TypeError('The `cleaned` parameter must be a list of strings')
            
            doc = cls.__clean(doc, cleaned)
        else:
            raise ValueError('If `clean` is True, you must provide a list in `cleaned` and the other way aroung')

        return doc
    
    @classmethod
    def to_html(cls, doc: str, *, cleaned: Optional[List[str]] = None) -> str:
        """
        This method transforms the plain text of a docstring into readable HTML format, 
        identifying and structuring each line as follows:

        Lines beginning with a hyphen and a space (`- `) are interpreted as list items and 
        enclosed within `<li>` tags grouped in an unordered list `<ul>`.

        **Notes:**
            - All other non-empty lines are encapsulated in paragraph tags `<p>`.

        Args:
            doc (str):
                Original text of the docstring to be formatted.
            cleaned (List[str], optional): 
                List of tokens to be removed using replace.

        Returns:
            str:
                HTML string resulting after applying the format.

        Raises:
            TypeError:
                If `cleaned` is provided but is not a list.
            ValueError:
                If `cleaned` is not provided.
        """
        if cleaned:
            if not isinstance(cleaned, list):
                raise TypeError('The `cleaned` parameter must be a list of strings')
            
            doc = cls.__clean(doc, cleaned)
        else:
            raise ValueError('If `clean` is True, you must provide a list in `cleaned` and the other way aroung')
        
        lines = cls.__get_lines(doc)

        out: List[str] = []
        in_list = False

        for line in lines:
            stripped = line.lstrip()

            if stripped.startswith("- "):
                if not in_list:
                    in_list = True
                    out.append("<ul>")

                out.append(f"<li>{stripped[2:]}</li>")
            else:
                if in_list:
                    in_list = False
                    out.append("</ul>")

                if line:
                    out.append(f"<p>{line}</p>")

        if in_list:
            out.append("</ul>")

        return "\n".join(out)

    @classmethod
    def __tabulation(cls, doc: str) -> str:
        """
        Adds a tab (`\\t`) at the beginning of each line of the received text.

        Args:
            doc (str):
                Text or docstring to be tabulated.

        Returns:
            str:
                Text with a tab applied at the beginning of each line.
        """
        lines = cls.__get_lines(doc)

        return '\n'.join(f'\t{line.strip()}' for line in lines)
    
    @classmethod
    def __clean(cls, doc: str, cleaned: List[str]) -> str:
        """
        Removes unwanted formatting characters from docstring text.

        Args:
            doc (str):
                Text or docstring to be cleaned.
            cleaned (List[str]): 
                List of tokens to be removed using replace.

        Returns:
            str:
                Text without special characters or formatting symbols.
        """
        lines = cls.__get_lines(doc)
        
        out: List[str] = []
        for line in lines:
            for token in cleaned:
                line = line.replace(token, '')
            
            out.append(line)
        
        return '\n'.join(out)

    @staticmethod
    def __get_lines(doc: str) -> List[str]:
        """
        Converts the text of the docstring into a list of processable lines.

        Removes whitespace at the beginning and end of the text, and separates
        the lines according to line breaks (`\\n`).

        Args:
            doc (str):
                Original text or docstring to be split.

        Returns:
            List[str]:
                List of lines obtained from the original text.
        """
        return doc.strip().splitlines()

# ---------------------------------------------------------------------------------------------------------------------
# END OF FILE