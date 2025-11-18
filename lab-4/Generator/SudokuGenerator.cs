// ============================================
// File: Generator/SudokuGenerator.cs
// ============================================
using System;
using System.Collections.Generic;
using System.Linq;
using SudokuCSP.Models;

namespace SudokuCSP.Generator
{
    /// <summary>
    /// Generates random valid 6×6 Sudoku puzzles
    /// </summary>
    public class SudokuGenerator
    {
        private static readonly Random random = new Random();
        private const int Size = Sudoku.Size;

        /// <summary>
        /// Generates a random valid 6×6 Sudoku puzzle with the specified difficulty
        /// </summary>
        /// <param name="cellsToRemove">Number of cells to remove (difficulty: 10-25 recommended)</param>
        /// <returns>A valid Sudoku puzzle grid</returns>
        public static int[,] Generate(int cellsToRemove = (int) (0.64 * Size * Size))
        {
            if (cellsToRemove < 0 || cellsToRemove > Sudoku.Size * Sudoku.Size)
                throw new ArgumentException($"Cells to remove must be between 0 and {Sudoku.Size * Sudoku.Size}");

            // Step 1: Create a filled valid Sudoku
            var grid = GenerateFilledSudoku();

            // Step 2: Remove cells to create puzzle
            RemoveCells(grid, cellsToRemove);

            return grid;
        }

        /// <summary>
        /// Generates a completely filled valid 6×6 Sudoku grid
        /// </summary>
        private static int[,] GenerateFilledSudoku()
        {
            var grid = new int[Size, Size];
            FillGrid(grid, 0, 0);
            return grid;
        }

        /// <summary>
        /// Recursively fills the grid with valid values using backtracking
        /// </summary>
        private static bool FillGrid(int[,] grid, int row, int col)
        {
            // Move to next row if we've filled current row
            if (col == Size)
            {
                row++;
                col = 0;
            }

            // If we've filled all rows, we're done
            if (row == Size)
                return true;

            // Get shuffled list of values to try
            var values = GetShuffledValues();

            foreach (int value in values)
            {
                if (IsValidPlacement(grid, row, col, value))
                {
                    grid[row, col] = value;

                    if (FillGrid(grid, row, col + 1))
                        return true;

                    grid[row, col] = 0; // Backtrack
                }
            }

            return false;
        }

        /// <summary>
        /// Removes specified number of cells from a filled grid
        /// </summary>
        private static void RemoveCells(int[,] grid, int count)
        {
            var positions = GetAllPositions().OrderBy(x => random.Next()).ToList();
            int removed = 0;

            foreach (var (row, col) in positions)
            {
                if (removed >= count)
                    break;

                if (grid[row, col] != 0)
                {
                    grid[row, col] = 0;
                    removed++;
                }
            }
        }

        /// <summary>
        /// Checks if placing a value at the given position is valid
        /// </summary>
        private static bool IsValidPlacement(int[,] grid, int row, int col, int value)
        {
            // Check row
            for (int c = 0; c < Size; c++)
                if (grid[row, c] == value)
                    return false;

            // Check column
            for (int r = 0; r < Size; r++)
                if (grid[r, col] == value)
                    return false;

            // Check block
            int blockRow = (row / Sudoku.BlockRows) * Sudoku.BlockRows;
            int blockCol = (col / Sudoku.BlockCols) * Sudoku.BlockCols;

            for (int r = blockRow; r < blockRow + Sudoku.BlockRows; r++)
                for (int c = blockCol; c < blockCol + Sudoku.BlockCols; c++)
                    if (grid[r, c] == value)
                        return false;

            return true;
        }

        /// <summary>
        /// Returns a shuffled list of values [1; Size]
        /// </summary>
        private static List<int> GetShuffledValues()
        {
            return Enumerable.Range(1, Size).OrderBy(x => random.Next()).ToList();
        }

        /// <summary>
        /// Returns all grid positions
        /// </summary>
        private static IEnumerable<(int row, int col)> GetAllPositions()
        {
            for (int row = 0; row < Size; row++)
                for (int col = 0; col < Size; col++)
                    yield return (row, col);
        }

        /// <summary>
        /// Generates a puzzle with predefined difficulty level
        /// </summary>
        public static int[,] GenerateEasy() => Generate((int) (0.42 * Size * Size));
        public static int[,] GenerateMedium() => Generate((int) (0.64 * Size * Size));
        public static int[,] GenerateHard() => Generate((int) (0.86 * Size * Size));
    }
}