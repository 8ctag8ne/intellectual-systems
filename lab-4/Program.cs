// ============================================
// File: Program.cs
// ============================================
using System;
using System.Diagnostics;
using SudokuCSP.Models;
using SudokuCSP.Solver;
using SudokuCSP.Generator;

namespace SudokuCSP
{
    /// <summary>
    /// Main console application entry point
    /// </summary>
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine($"=== {Sudoku.Size}×{Sudoku.Size} Sudoku CSP Solver ===\n");

            int[,] puzzle;

            // Ask user if they want a random puzzle
            Console.Write("Generate random puzzle? (y/n): ");
            bool generateRandom = Console.ReadLine()?.Trim().ToLower() == "y";

            if (generateRandom)
            {
                Console.WriteLine("\nSelect difficulty:");
                Console.WriteLine("  1 - Easy (42% of empty cells)");
                Console.WriteLine("  2 - Medium (64% of empty cells)");
                Console.WriteLine("  3 - Hard (86% of empty cells)");
                Console.Write("Enter choice (1-3): ");
                
                string? choice = Console.ReadLine()?.Trim();
                
                puzzle = choice switch
                {
                    "1" => SudokuGenerator.GenerateEasy(),
                    "2" => SudokuGenerator.GenerateMedium(),
                    "3" => SudokuGenerator.GenerateHard(),
                    _ => SudokuGenerator.GenerateMedium() // Default to medium
                };

                Console.WriteLine($"\nGenerated {GetDifficultyName(choice!)} puzzle!\n");
            }
            else
            {
                // Use predefined test puzzle
                puzzle = new int[,]
                {
                    { 0, 0, 0, 2, 0, 0 },
                    { 1, 2, 0, 0, 0, 0 },
                    { 0, 3, 1, 0, 0, 0 },
                    { 0, 0, 0, 3, 0, 0 },
                    { 0, 0, 0, 0, 0, 0 },
                    { 0, 0, 0, 0, 0, 0 }
                };
            }

            var sudoku = new Sudoku(puzzle);
            
            Console.WriteLine("Initial puzzle:");
            sudoku.Print();

            // Get heuristic preferences
            Console.Write("Enable MRV (Minimum Remaining Values)? (y/n): ");
            bool useMRV = Console.ReadLine()?.Trim().ToLower() == "y";

            Console.Write("Enable Degree heuristic? (y/n): ");
            bool useDegree = Console.ReadLine()?.Trim().ToLower() == "y";

            Console.Write("Enable LCV (Least Constraining Value)? (y/n): ");
            bool useLCV = Console.ReadLine()?.Trim().ToLower() == "y";

            Console.WriteLine($"\nSolving with heuristics: MRV={useMRV}, Degree={useDegree}, LCV={useLCV}");
            
            var stopwatch = Stopwatch.StartNew();
            var solver = new CspSolver(sudoku, useMRV, useDegree, useLCV);
            bool solved = solver.Solve();
            stopwatch.Stop();

            Console.WriteLine($"  Time elapsed: {stopwatch.ElapsedMilliseconds}ms\n");

            if (solved)
            {
                Console.WriteLine("Solution found:");
                sudoku.Print();
            }
            else
            {
                Console.WriteLine("No solution exists.");
            }

            Console.WriteLine("\nPress any key to exit...");
            Console.ReadKey();
        }

        private static string GetDifficultyName(string choice)
        {
            return choice switch
            {
                "1" => "Easy",
                "2" => "Medium",
                "3" => "Hard",
                _ => "Medium"
            };
        }
    }
}