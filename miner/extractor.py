import re

def clean_and_split_name(name):
    """
    Toma un nombre de función (ej. make_response o retainAll) 
    y lo divide en palabras base en minúsculas.
    """
    name = name.replace('_', ' ')
    
    name = re.sub(r'([A-Z])', r' \1', name)
    
    words = name.lower().split()
    
    return [w for w in words if len(w) > 1]

def extract_words_from_code(code, language):
    """
    Busca declaraciones de funciones/métodos en el código fuente.
    """
    words_found = []
    
    if language == 'python':
        pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, code)
        for match in matches:
            words_found.extend(clean_and_split_name(match))
            
    elif language == 'java':
        pattern = r'(?:public|protected|private)\s+(?:[\w\<\>\[\]]+\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, code)
        for match in matches:
            words_found.extend(clean_and_split_name(match))
            
    return words_found