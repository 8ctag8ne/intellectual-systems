using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata.Ecma335;

namespace SudokuCSP.Models
{
    /// <summary>
    /// Manages the 6×6 Sudoku grid with 2×3 blocks
    /// </summary>
    public class Sudoku
    {
        public const int Size = 6;
        public const int BlockRows = 2;
        public const int BlockCols = 3;
        
        private int[,] grid;

        public Sudoku(int[,] initialGrid)
        {
            if (initialGrid.GetLength(0) != Size || initialGrid.GetLength(1) != Size)
                throw new ArgumentException($"Grid must be {Size}×{Size}");
            
            grid = (int[,])initialGrid.Clone();
        }

        public int GetValue(int row, int col) => grid[row, col];
        
        public void SetValue(int row, int col, int value) => grid[row, col] = value;

        public IEnumerable<int> GetRow(int row)
        {
            for (int col = 0; col < Size; col++)
                yield return grid[row, col];
        }

        public IEnumerable<int> GetColumn(int col)
        {
            for (int row = 0; row < Size; row++)
                yield return grid[row, col];
        }

        public IEnumerable<int> GetBlock(int row, int col)
        {
            int blockRow = (row / BlockRows) * BlockRows;
            int blockCol = (col / BlockCols) * BlockCols;

            for (int r = blockRow; r < blockRow + BlockRows; r++)
                for (int c = blockCol; c < blockCol + BlockCols; c++)
                    yield return grid[r, c];
        }

        public bool IsValidPlacement(int row, int col, int value)
        {
            if (value < 1 || value > Size) return false;

            return !GetRow(row).Where(v => v != 0).Contains(value) &&
                   !GetColumn(col).Where(v => v != 0).Contains(value) &&
                   !GetBlock(row, col).Where(v => v != 0).Contains(value);
        }

        public IEnumerable<(int row, int col)> GetNeighbors(int row, int col)
        {
            // Row neighbors
            for (int c = 0; c < Size; c++)
                if (c != col) yield return (row, c);

            // Column neighbors
            for (int r = 0; r < Size; r++)
                if (r != row) yield return (r, col);

            // Block neighbors
            int blockRow = (row / BlockRows) * BlockRows;
            int blockCol = (col / BlockCols) * BlockCols;

            for (int r = blockRow; r < blockRow + BlockRows; r++)
            {
                for (int c = blockCol; c < blockCol + BlockCols; c++)
                {
                    if (r != row && c != col)
                        yield return (r, c);
                }
            }
        }

        public void Print()
        {
            // Console.WriteLine("  " + string.Join(" ", Enumerable.Range(0, Size)));
            string header = string.Empty;

            header += "  ";
            for(int i = 0; i <Size; i++)
            {
                header += $"{i} ";
                if ((i + 1) % BlockCols == 0)
                {
                    header += "  ";
                }
            }
            header = header.TrimEnd();
            Console.WriteLine(header);
            Console.WriteLine("  " + new string('-', header.Length - 2));
            
            for (int row = 0; row < Size; row++)
            {
                Console.Write(row + "|");
                for (int col = 0; col < Size; col++)
                {
                    int value = grid[row, col];
                    Console.Write(value == 0 ? "." : value.ToString());
                    if (col < Size - 1) Console.Write(" ");
                    if ((col + 1) % BlockCols == 0) Console.Write("| ");
                }
                Console.WriteLine();
                
                if ((row + 1) % BlockRows == 0)
                    Console.WriteLine("  " + new string('-', header.Length - 2));
            }
            Console.WriteLine();
        }

    }
}