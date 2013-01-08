'''
Created on Jan 8, 2013

@author: tulvur
'''
import re

class OccurrencesCounter(object):
    """Class intended to help analyzing traces from a file"""
    
    def __init__(self, filepath, pattern):
        self.pattern = re.compile(pattern)
        self.filepath = filepath
    
    def _read_file(self):
        with open(self.filepath, 'r') as f:
            return f.read()
    
    def count_occurrences(self):
        string = self._read_file()
        return len(self.pattern.findall(string))
            
        
    def print_occurrences(self):
        string = self._read_file()
        for occurrence in self.pattern.findall(string):
            print occurrence

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze traces from a file.')
    parser.add_argument('file', help='Specify the path of the file to be analyzed.')
    parser.add_argument('pattern', help='Specify the pattern whose occurrences you want to search in the file.')
    # Pattern examples:
    #    "/whitepage/clues/\w+" or simply "whitepage/clues/"
    #    "/whitepage/clues\s+"
    #    "/query"
    
    args = parser.parse_args()
    o = OccurrencesCounter(args.file, args.pattern)
    print o.count_occurrences()
    #o.print_occurrences()