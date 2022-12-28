
class LatexParsingError(Exception):
    # For errors parsing user-provided latex markup
    pass

class FileTypeError(Exception):
    # For errors arising from an unsupported or unexpected file type
    pass

class FileParsingError(Exception):
    # For errors parsing a file
    pass

class MarkdownParsingError(Exception):
    pass