import { describe, it, expect } from 'vitest';
import { detectLanguage, SUPPORTED_LANGUAGES } from '../utils/languageDetector';

describe('Language Detector & Registry', () => {
  it('defines all 9 supported languages', () => {
    const ids = SUPPORTED_LANGUAGES.map((l) => l.id);
    expect(ids).toEqual([
      'python',
      'java',
      'javascript',
      'typescript',
      'c',
      'cpp',
      'html',
      'css',
      'sql',
    ]);
  });

  it('detects Python code', () => {
    expect(detectLanguage('def test_func():\n    print("hello")')).toBe('python');
    expect(detectLanguage('import os\nfrom sys import path')).toBe('python');
  });

  it('detects Java code', () => {
    expect(detectLanguage('public class OrderManager {\n    public static void main(String[] args) {\n        System.out.println("Started");\n    }\n}')).toBe('java');
  });

  it('detects JavaScript code', () => {
    expect(detectLanguage('const add = (a, b) => {\n  console.log("summing");\n  return a + b;\n};')).toBe('javascript');
  });

  it('detects TypeScript code', () => {
    expect(detectLanguage('interface User {\n  id: string;\n  name: string;\n}\nconst u: User = { id: "1", name: "Alice" };')).toBe('typescript');
  });

  it('detects C code', () => {
    expect(detectLanguage('#include <stdio.h>\n#include <stdlib.h>\nint main() {\n  printf("hello\\n");\n  return 0;\n}')).toBe('c');
  });

  it('detects C++ code', () => {
    expect(detectLanguage('#include <iostream>\n#include <vector>\nint main() {\n  std::cout << "hello" << std::endl;\n  return 0;\n}')).toBe('cpp');
  });

  it('detects HTML markup', () => {
    expect(detectLanguage('<!DOCTYPE html>\n<html><body><h1>Title</h1></body></html>')).toBe('html');
  });

  it('detects CSS styles', () => {
    expect(detectLanguage('.container {\n  display: flex;\n  background: #0f172a;\n  padding: 1rem;\n}')).toBe('css');
  });

  it('detects SQL queries', () => {
    expect(detectLanguage('SELECT id, name FROM users WHERE role = "admin" ORDER BY created_at DESC;')).toBe('sql');
  });

  it('returns null for empty or unrecognized input', () => {
    expect(detectLanguage('')).toBeNull();
    expect(detectLanguage('   ')).toBeNull();
    expect(detectLanguage('42')).toBeNull();
  });
});
