Leo Language 🦁
Leo is a lightweight, interpreted programming language designed for simplicity and educational purposes. It features a built-in professional IDE with syntax highlighting, line numbering, and a unique bridge to C# (.NET) libraries.
🖥️ IDE Features
Modern UI: Dark-themed editor inspired by VS Code.
Syntax Highlighting: Visual distinction for logic, types, strings, and comments.
Line Numbering: Easy navigation through your code.
One-Click Build: Integrated C# compiler (invokes csc.exe) to create .dll modules instantly.
📜 Language Syntax
Data Types & Variables
Variables are declared by specifying the type (optional for assignment) followed by the value.
leo
float pi = 3,14
int radius = 10
str name = "Leo Project"
bool isActive = true

## Quick Start if you get NPM
1. Install: `npm install -g leo-lang-uzwerg-lfn`
2. Run IDE: `leo-ide` (or `python intre.py`)

Basic I/O
type="text": Prints a string to the console.
typeval=variable: Prints the value of a specific variable.
input("prompt"): Opens a dialog box to receive user input.
leo
str user = input("Enter your name: ")
type="Welcome, "
typeval=user

Math & Logic
Operators: +, -, *, /, % (modulo).
Power: @ (e.g., 2 @ 3 is 8).
Comparison: CMP (equivalent to ==).
Control Flow:
if [condition] right [action]
DLYA [count] [action] (Loop for N times)
END (Terminates the program)
leo
int x = 10
if x CMP 10 right type="X is ten!"
DLYA 3 type="This will print 3 times"

Comments
[]: Single-line comment.
| |: Multi-line comment.
🧩 C# Integration (Libraries)
Leo allows you to extend its functionality using C# modules.
Create a C# file (lib.cs) with public static methods:
csharp
namespace LeoPlugins {
    public class Utils {
        public static string SayHello(string name) => "Hello, " + name;
    }
}


Build: Click "СБОРКА C#" in the IDE to generate MyLib.dll.
Import in Leo: Use the drop command.
leo
drop "MyLib.dll" LeoPlugins.Utils
str res = Utils.SayHello("User")
typeval=res


🚀 Getting Started
Prerequisites
Python 3.x
pythonnet library:
bash
pip install pythonnet


Windows OS: Uses built-in .NET Framework for C# compilation.
Installation
Clone the repository.
Run the main script:
bash
python leo_ide.py


🛠️ Interface Translation (RU -> EN)
Since the IDE interface is currently in Russian, here is a quick reference:
▶ ЗАПУСК: Run Code
🔨 СБОРКА C#: Build C# Library (lib.cs -> MyLib.dll)
Консоль: Output Console
