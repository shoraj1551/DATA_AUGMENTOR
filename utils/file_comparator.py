import pandas as pd
import json
from typing import Dict, List, Tuple, Any


def compare_csv(file1_content: str, file2_content: str, file1_name: str = "File 1", file2_name: str = "File 2") -> Dict[str, Any]:
    """
    Compare two CSV files.
    
    Returns:
        Dictionary with comparison results
    """
    try:
        df1 = pd.read_csv(pd.io.common.StringIO(file1_content))
    except Exception as e:
        raise ValueError(f"Error parsing CSV in '{file1_name}': {str(e)}")
    
    try:
        df2 = pd.read_csv(pd.io.common.StringIO(file2_content))
    except Exception as e:
        raise ValueError(f"Error parsing CSV in '{file2_name}': {str(e)}")
    
    try:
        # Convert to sets of tuples for comparison
        set1 = set(df1.apply(tuple, axis=1))
        set2 = set(df2.apply(tuple, axis=1))
        
        only_in_file1 = set1 - set2
        only_in_file2 = set2 - set1
        common = set1 & set2
        
        # Convert back to readable format
        def format_row(row_tuple):
            return " | ".join(str(x) for x in row_tuple)
        
        return {
            "only_in_file1": [format_row(row) for row in only_in_file1],
            "only_in_file2": [format_row(row) for row in only_in_file2],
            "common": [format_row(row) for row in common],
            "stats": {
                "total_file1": len(df1),
                "total_file2": len(df2),
                "only_in_file1": len(only_in_file1),
                "only_in_file2": len(only_in_file2),
                "common": len(common)
            }
        }
    except Exception as e:
        raise ValueError(f"Error comparing CSV files: {str(e)}")


def compare_txt(file1_content: str, file2_content: str, file1_name: str = "File 1", file2_name: str = "File 2") -> Dict[str, Any]:
    """
    Compare two text files line by line.
    
    Returns:
        Dictionary with comparison results
    """
    lines1 = set(file1_content.strip().split('\n'))
    lines2 = set(file2_content.strip().split('\n'))
    
    only_in_file1 = lines1 - lines2
    only_in_file2 = lines2 - lines1
    common = lines1 & lines2
    
    return {
        "only_in_file1": sorted(list(only_in_file1)),
        "only_in_file2": sorted(list(only_in_file2)),
        "common": sorted(list(common)),
        "stats": {
            "total_file1": len(lines1),
            "total_file2": len(lines2),
            "only_in_file1": len(only_in_file1),
            "only_in_file2": len(only_in_file2),
            "common": len(common)
        }
    }


def compare_json(file1_content: str, file2_content: str, file1_name: str = "File 1", file2_name: str = "File 2") -> Dict[str, Any]:
    """
    Compare two JSON files.
    
    Returns:
        Dictionary with comparison results
    """
    try:
        json1 = json.loads(file1_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON in '{file1_name}': {str(e)}")
    
    try:
        json2 = json.loads(file2_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing JSON in '{file2_name}': {str(e)}")
    
    try:
        # Convert to strings for comparison
        if isinstance(json1, list) and isinstance(json2, list):
            # Compare as lists
            set1 = set(json.dumps(item, sort_keys=True) for item in json1)
            set2 = set(json.dumps(item, sort_keys=True) for item in json2)
        elif isinstance(json1, dict) and isinstance(json2, dict):
            # Compare keys and values
            set1 = set(f"{k}: {json.dumps(v, sort_keys=True)}" for k, v in json1.items())
            set2 = set(f"{k}: {json.dumps(v, sort_keys=True)}" for k, v in json2.items())
        else:
            # Direct comparison
            set1 = {json.dumps(json1, sort_keys=True)}
            set2 = {json.dumps(json2, sort_keys=True)}
        
        only_in_file1 = set1 - set2
        only_in_file2 = set2 - set1
        common = set1 & set2
        
        return {
            "only_in_file1": sorted(list(only_in_file1)),
            "only_in_file2": sorted(list(only_in_file2)),
            "common": sorted(list(common)),
            "stats": {
                "total_file1": len(set1),
                "total_file2": len(set2),
                "only_in_file1": len(only_in_file1),
                "only_in_file2": len(only_in_file2),
                "common": len(common)
            }
        }
    except Exception as e:
        raise ValueError(f"Error comparing JSON files: {str(e)}")


def compare_files(file1_path: str, file2_path: str, file1_content: str, file2_content: str) -> Dict[str, Any]:
    """
    Main comparison function that routes to appropriate comparator based on file type.
    
    Args:
        file1_path: Path/name of first file
        file2_path: Path/name of second file
        file1_content: Content of first file
        file2_content: Content of second file
        
    Returns:
        Dictionary with comparison results
    """
    # Detect file type
    ext1 = file1_path.lower().split('.')[-1]
    ext2 = file2_path.lower().split('.')[-1]
    
    if ext1 != ext2:
        raise ValueError(f"File types must match. '{file1_path}' is {ext1.upper()} but '{file2_path}' is {ext2.upper()}")
    
    if ext1 == 'csv':
        return compare_csv(file1_content, file2_content, file1_path, file2_path)
    elif ext1 == 'txt':
        return compare_txt(file1_content, file2_content, file1_path, file2_path)
    elif ext1 == 'json':
        return compare_json(file1_content, file2_content, file1_path, file2_path)
    else:
        raise ValueError(f"Unsupported file type: {ext1.upper()}. Supported types: CSV, TXT, JSON")

